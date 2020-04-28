# <font color=#009900>guitest</font>
This project will build a tool for automatic test of RRTE (FCG Tool) with pywin32.  

---
## <font color=#009900>项目概要</font>    

---
## <font color=#009900>Windows图形界面程序自动测试</font>    

### <font color=#009900>pywin32的安装</font>   
本来想使用腾讯的QT4C测试框架，但是发现该框架很不稳定，尤其是注释多用中文，对于系统的适用性很差，因此决定直接使用QT4C底层所调用的pywin32，该项目由澳洲的一位牛人————Mark Hammond mhammond编写，能够通过python访问windows的API。  
pywin32符合Python Software Foundation License。  

安装pywin32直接用pip安装容易失败，不如直接从下列网址下载：  
[pywin32下载站点](https://github.com/mhammond/pywin32/releases)  
下载那个和自己python版本相同，和OS位数相同的程序，然后安装即可。  
然后爱需要安装win32api。  
```shell
python.exe Scripts/pywin32_postinstall.py -install
```
如果全部安装成功的话，在python命令行界面应该可以导入下列两个包。  
```python
import win32api
import win32con
```


### <font color=#009900>pywin32学习摘要</font>   

---
## <font color=#009900>参考资料</font>   
[PyWin32文档](http://timgolden.me.uk/pywin32-docs/)  
[PyWin32文档部分中文译文](https://blog.csdn.net/wang13342322203/article/details/81280377)  
[Automating Windows Applications Using COM](https://pbpython.com/windows-com.html)  
[QT4C项目](https://github.com/Tencent/QT4C)  
[QT4C/Demo项目](https://github.com/qtacore/QT4CDemoProj)  
[QT4C说明书](https://qt4c.readthedocs.io/zh_CN/latest/setup.html)   

QT4C的安装，运行Demo（前提是要安装pywin32）：  
```shell
pip install qtaf
pip install qt4c
git clone https://github.com/qtacore/QT4CDemoProj.git
python manage.py runscript demotest/hello.py