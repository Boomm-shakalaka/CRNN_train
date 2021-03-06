#python train.py --adadelta --trainRoot ./data/lmdb/ --valRoot ./data/lmdb/ --cuda
from __future__ import print_function
from __future__ import division
import argparse
import random
import torch
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data
from torch.autograd import Variable
import numpy as np
from warpctc_pytorch import CTCLoss
import os
import utils
import dataset
import matplotlib.pyplot as plt
import models.crnn as crnn

parser = argparse.ArgumentParser()
parser.add_argument('--trainRoot', required=True, help='path to dataset')
parser.add_argument('--valRoot', required=True, help='path to dataset')
parser.add_argument('--workers', type=int, help='number of data loading workers', default=0)#线程数导入数据
parser.add_argument('--batchSize', type=int, default=128, help='input batch size')#512
parser.add_argument('--valbatchSize', type=int, default=256, help='input batch size')#512
parser.add_argument('--imgH', type=int, default=32, help='the height of the input image to network')
parser.add_argument('--imgW', type=int, default=100, help='the width of the input image to network')
parser.add_argument('--nh', type=int, default=256, help='size of the lstm hidden state')
parser.add_argument('--nepoch', type=int, default=400, help='number of epochs to train for')
parser.add_argument('--cuda', action='store_true', help='enables cuda')
parser.add_argument('--ngpu', type=int, default=1, help='number of GPUs to use')
parser.add_argument('--pretrained', default='', help="path to pretrained model (to continue training)")
parser.add_argument('--alphabet', type=str, default='中華民國年月日0123456789')#零壹貳叁肆伍陸柒捌玖拾佰仟萬億整元
parser.add_argument('--expr_dir', default='expr', help='Where to store samples and models')
#parser.add_argument('--displayInterval', type=int, default=10, help='Interval to be displayed')#设置多少次迭代显示一次
#parser.add_argument('--n_val_disp', type=int, default=10, help='Number of samples to display when test')#每次验证显示的个数
parser.add_argument('--valInterval', type=int, default=1, help='Interval to be displayed')#设置多少次迭代验证一次
parser.add_argument('--saveInterval', type=int, default=1, help='Interval to be displayed')#保存模型
parser.add_argument('--lr', type=float, default=0.01, help='learning rate for Critic, not used by adadealta')
parser.add_argument('--beta1', type=float, default=0.5, help='beta1 for adam. default=0.5')
parser.add_argument('--adam', action='store_true', help='Whether to use adam (default is rmsprop)')
parser.add_argument('--adadelta', action='store_true', help='Whether to use adadelta (default is rmsprop)')
parser.add_argument('--keep_ratio', action='store_true', help='whether to keep ratio for image resize')
parser.add_argument('--manualSeed', type=int, default=1234, help='reproduce experiemnt')
parser.add_argument('--random_sample', action='store_true', help='whether to sample the dataset with random sampler')
opt = parser.parse_args()
#print(opt)
def val(net, dataset, criterion, max_iter=100):
    print('Start val')

    for p in crnn.parameters():
        p.requires_grad = False

    net.eval()
    data_loader = torch.utils.data.DataLoader(
        dataset, shuffle=True, batch_size=opt.batchSize, num_workers=int(opt.workers))
    val_iter = iter(data_loader)

    i = 0
    n_correct = 0
    loss_avg = utils.averager()
    #max_iter = min(max_iter, len(data_loader))
    max_iter=int(len(data_loader))
    for i in range(max_iter):
        data = val_iter.next()
        i += 1
        cpu_images, cpu_texts = data
        batch_size = cpu_images.size(0)
        utils.loadData(image, cpu_images)
        t, l = converter.encode(cpu_texts)
        utils.loadData(text, t)
        utils.loadData(length, l)

        preds = crnn(image)
        preds_size = Variable(torch.IntTensor([preds.size(0)] * batch_size))
        cost = criterion(preds, text, preds_size, length) / batch_size
        loss_avg.add(cost)

        _, preds = preds.max(2)
        #preds = preds.squeeze(2)
        preds = preds.transpose(1, 0).contiguous().view(-1)
        sim_preds = converter.decode(preds.data, preds_size.data, raw=False)
        for pred, target in zip(sim_preds, cpu_texts):
            if pred == target.lower():
                n_correct += 1

    #raw_preds = converter.decode(preds.data, preds_size.data, raw=True)[:opt.n_val_disp]
    #for raw_pred, pred, gt in zip(raw_preds, sim_preds, cpu_texts):
        #print('%-20s => %-20s, gt: %-20s' % (raw_pred, pred, gt))
    loss_val = loss_avg.val()

    if float(max_iter * opt.batchSize)!=0:
        accuracy = n_correct / float(max_iter * opt.batchSize)

        print('Val loss: %f, accuracy: %f' % (loss_val, accuracy))
        return accuracy,loss_val
    else:
        return 0, loss_val


def trainBatch(net, criterion, optimizer):
    data = train_iter.next()
    cpu_images, cpu_texts = data
    batch_size = cpu_images.size(0)
    utils.loadData(image, cpu_images)
    t, l = converter.encode(cpu_texts)
    utils.loadData(text, t)
    utils.loadData(length, l)

    preds = crnn(image)
    preds_size = Variable(torch.IntTensor([preds.size(0)] * batch_size))
    cost = criterion(preds, text, preds_size, length) / batch_size
    crnn.zero_grad()
    cost.backward()
    optimizer.step()
    return cost

# custom weights initialization called on crnn
def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        m.weight.data.normal_(1.0, 0.02)
        m.bias.data.fill_(0)

if not os.path.exists(opt.expr_dir):
    os.makedirs(opt.expr_dir)
random.seed(opt.manualSeed)
np.random.seed(opt.manualSeed)
torch.manual_seed(opt.manualSeed)
cudnn.benchmark = True
if torch.cuda.is_available() and not opt.cuda:
    print("WARNING: You have a CUDA device, so you should probably run with --cuda")

train_dataset = dataset.lmdbDataset(root=opt.trainRoot)
assert train_dataset
if not opt.random_sample and 0:
    sampler = dataset.randomSequentialSampler(train_dataset, opt.batchSize)
else:
    sampler = None
train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=opt.batchSize,
    shuffle=True, sampler=sampler,
    num_workers=int(opt.workers),
    collate_fn=dataset.alignCollate(imgH=opt.imgH, imgW=opt.imgW, keep_ratio=opt.keep_ratio))
val_dataset = dataset.lmdbDataset(
    root=opt.valRoot, transform=dataset.resizeNormalize((100, 32)))

nclass = len(opt.alphabet) + 1
nc = 1

converter = utils.strLabelConverter(opt.alphabet)
criterion = CTCLoss()


crnn = crnn.CRNN(opt.imgH, nc, nclass, opt.nh)
crnn.apply(weights_init)
if opt.pretrained != '':
    import collections
    print('loading pretrained model from %s' % opt.pretrained)

    load_model_ = torch.load(opt.pretrained)
    # for k, v in load_model_.items():
    #     print(k,"  ::shape",v.shape)

    state_dict_rename = collections.OrderedDict()
    for k, v in load_model_.items():
        name = k[7:]  # remove `module.`
        state_dict_rename[name] = v

    crnn.load_state_dict(state_dict_rename)
print(crnn)

image = torch.FloatTensor(opt.batchSize, 1, opt.imgH, opt.imgW)
text = torch.IntTensor(opt.batchSize * 10)
length = torch.IntTensor(opt.batchSize)

if opt.cuda:
    crnn.cuda()
    crnn = torch.nn.DataParallel(crnn, device_ids=range(opt.ngpu))
    image = image.cuda()
    criterion = criterion.cuda()

image = Variable(image)
text = Variable(text)
length = Variable(length)

# loss averager
loss_avg = utils.averager()

# setup optimizer
if opt.adam:
    optimizer = optim.Adam(crnn.parameters(), lr=opt.lr,
                           betas=(opt.beta1, 0.999))
elif opt.adadelta:
    optimizer = optim.Adadelta(crnn.parameters())
else:
    optimizer = optim.RMSprop(crnn.parameters(), lr=opt.lr)

time_epoch=[]
val_y=[]
loss_y=[]
train_loss=[]
fig, ax_acc = plt.subplots()
ax_acc.set_title('lr={},batch_size={}'.format(str(opt.lr),str(opt.batchSize)),fontsize=12,color='r')
ax_loss = ax_acc.twinx()
ax_loss_train = ax_acc.twinx()
for epoch in range(opt.nepoch):
    train_iter = iter(train_loader)
    i = 0
    while i < len(train_loader):
        for p in crnn.parameters():
            p.requires_grad = True
        crnn.train()

        cost = trainBatch(crnn, criterion, optimizer)
        loss_avg.add(cost)
        i += 1
    loss_avg_train=loss_avg.val()
        #if i % opt.displayInterval == 0:
    print('[%d/%d][%d/%d] Loss: %f' %
          (epoch, opt.nepoch, i, len(train_loader),loss_avg_train ))
    loss_avg.reset()
        # do checkpointing
        # if i % opt.saveInterval == 0:
        #     torch.save(crnn.state_dict(), '{0}/netCRNN_{1}_{2}.pth'.format(opt.expr_dir, epoch, i))

    if (0 != epoch) and (epoch % opt.saveInterval==0):
        torch.save(
            crnn.state_dict(), '{0}/netCRNN_{1}_{2}.pth'.format(opt.expr_dir, epoch, i))
        time_epoch.append(epoch)
        val_accuracy ,loss_= val(crnn, val_dataset, criterion)
        train_loss.append(loss_avg_train)
        val_y.append(val_accuracy)
        loss_y.append(loss_)
    if epoch % opt.valInterval == 0:
        ax_acc.plot(time_epoch,val_y,c='red',marker='.',label='Val_acc')
        ax_acc.set_xlabel("n-epoch")
        ax_acc.set_ylabel("accuracy")
        ax_loss.plot(time_epoch,loss_y, c='blue', marker='.',label='Val_loss')
        #ax_loss.set_ylabel("val_loss")
        ax_loss_train.plot(time_epoch, train_loss, c='yellow', marker='.',label='Train_loss')
        #ax_loss_train.set_ylabel("train_loss")
        for x,y in zip(time_epoch,val_y):
            ax_acc.text(x,y,'%.3f' % y,fontdict={'fontsize':5})
        for x,y in zip(time_epoch,loss_y):
            ax_loss.text(x,y,'%.3f' % y,fontdict={'fontsize':5})
        for x,y in zip(time_epoch,train_loss):
            ax_loss_train.text(x,y,'%.3f' % y,fontdict={'fontsize':5})
        plt.savefig("log.png")


