# CRNN

## Reference
1. 源码：https://github.com/meijieru/crnn.pytorch
2. bug修改版：https://github.com/wuzuowuyou/crnn_pytorch(最终使用)
3. csdn:https://blog.csdn.net/yang332233/article/details/114681470  
4. lmdb训练集制作:https://blog.csdn.net/weixin_30727835/article/details/95614996
------ 
## Environment
    ubuntu18.04+cuda10+pytorch1.2+pycharm+anaconda
	lmdb==0.97
	numpy==1.17.2
	Pillow==6.1.0
	six==1.12.0
	torch==1.2.0
	torchvision==0.4.0
------ 
## Demo
1. 建立训练集和验证集，例如1.jpg对应1.txt。.txt中是图片中的文本。
2. 运行Tolmdb.py，生成LMDB数据
3. 运行

 
   
4. 本系统分为单张识别和批量识别模式，点击开始识别将调用。点击单张识别，通过可视化路径选择所要辨识的支票图片，再点击开始识别，系统会对支票自动进行辨识，并将文本结果输出到    左边显示框，并且在支票图像展示区域也会框选识别目标。使用者可以点击保存信息，将这次的识别结果先保存于后台。当遇到大量支票需要辨识时，可以选择批量识别模式，选择所要辨识    的支票文件夹，所有支票文件名会先显示在信息交互窗口。再点击开始识别，系统开始自动辨识，每张支票大概只消耗 2-3 秒的时间。等待辨识结束，可以点击保存信息将结果存于后台。  
   
   ![alt 文字](https://github.com/Boomm-shakalaka/CheckRecognition_TW/blob/master/demo_pic/recog.png)
   
5. 当所有辨识结果已经保存，可以点击上方导出按钮，系统会自动将已保存的支票信息生成一份 Excel 档案，以提供给用户进行后期使用。
