# Shell

在命令行输出命令"python main.py"即可启动程序。解释器版本为3.7.6.

从终端接受命令，模拟系统调用，使用内核功能，返回结果。

|cmd|function|
|:---:| :---:|
| cr \<name\> \<\priority>\{1,2\}| 创建进程|
| de \<name\>| 删除进程|
| req \<resource name\> \<of units\>|请求资源 |
| rel \<resource name\> \<of units\>|释放资源 |
| to| 手动时间片轮转 |
| list ready（list可使用ls代替） | 列出就绪队列中的所有进程并显示其状态 |
| list block 、 list b | 列出阻塞队列进程|
| list res| 列出所有可使用的资源|
| exit|退出shell |
|read \<filename\>  | 读取txt文件内容作为命令集，每行一条输入|

具体代码部分在实验报告中已经详细说明，这里不再赘述。