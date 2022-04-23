# CRNN

## Reference
1. 源码：https://github.com/meijieru/crnn.pytorch
2. bug修改版：https://github.com/wuzuowuyou/crnn_pytorch(最终使用)
3. csdn:https://blog.csdn.net/yang332233/article/details/114681470  
4. lmdb训练集制作:https://blog.csdn.net/weixin_30727835/article/details/95614996
------ 
## Environment
 	```
    ubuntu18.04+cuda10+pytorch1.2+pycharm+anaconda
	lmdb==0.97
	numpy==1.17.2
	Pillow==6.1.0
	six==1.12.0
	torch==1.2.0
	torchvision==0.4.0
 	```
------ 
## Demo
1. 建立训练集和验证集，例如1.jpg对应1.txt。.txt中是图片中的文本。
2. 运行 lmdb.py，生成LMDB数据。
3. 修改 train.py中的alphabet和参数。运行 train.py，开始训练。    
------ 
## Debug
1. run lmdb.py     
	Error: 'utf-8' codec can't decode byte 0xff in position 0: inva    
	解决：在python2才能运行

2. warp-ctc编译：  
 	```
	git clone https://github.com/SeanNaren/warp-ctc.git
	cd warp-ctc    
	mkdir build     
	cd build    
	cmake ..  
	make
	cd ../pytorch_binding
	python setup.py install
	 ```
  	Error: nvcc fatal : Value 'c++14' is not defined for option 'std      
   	解决： cuda版本兼容问题，安装cuda10,cudnn7,torch1.2,python3.6```conda install pytorch==1.2.0,torchvision==0.4.0 cudatoolkit=10.0 -c pytorch ```  
	
	Error: fatal error: cuda_runtime_api.h: No such file or directory  
	解决：在warp-ctc/pytorch_binding/setup.py 修改  ```extra_compile_args = ['-std=c++14', '-fPIC']为extra_compile_args = ['-std=c++14', '-fPIC','-I/usr/local/cuda/include'] ```  
	
3. train.py：  
	Error: the nvidia driver on your system is too old (found version 9000)  
	解决：显卡驱动版本过低，或者cuda,pytorch版本没有对应。  
	1. 安装对应版本。  
	2. 重新安装新版显卡驱动（https://zhuanlan.zhihu.com/p/59618999）  

4. 中文汉字训练：  
	Error: TypeError: function takes exactly 5 arguments (1 given)  
	解决： 无人解答。parser.add_argument('--workers', type=int, help='number of data loading workers',default=0)#线程数导入数据，default为0    
	
	Error: UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd9 in position 0: invalid continuation byte  
	解决： 无人解答，中文字符解码问题（猜测）
        解决：dataset.py-> label = label_byte.decode('gbk')。gb2312简体汉字编码规范，big5繁体汉字编码规范,gbk大字符集，兼容所有亚洲字符。但针对繁体字这边只能用gbk不知道为什么
