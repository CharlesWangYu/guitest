import subprocess
import uiautomation
import time

#打开计算器程序
subprocess.Popen('C:\Users\30019613\AppData\Local\Google\Chrome\Application\chrome.exe')
time.sleep(2)

#通过UIAutomation定位窗体
calcwindow = uiautomation.WindowControl(searchDepth=1, Name='新标签页 - Google Chrome')

#在最上层显示
calcwindow.SetTopmost(True)

#点击数字“7”
#calcwindow.ButtonControl(Name='7').Click()

#点击加号
#calcwindow.ButtonControl(Name='加').Click()

#点击数字“5”
#calcwindow.ButtonControl(Name='5').Click()

#点击等号
#calcwindow.ButtonControl(Name='等于').Click()

#获取数据显示框的内容
#result = calcwindow.TextControl(AutomationId="158")
#print(result.Name)

#做验证
#if result.Name.split(' ')[0] == '12':
#	print("测试成功.")
#else:
#	print("测试失败.")
#time.sleep(2)

#关闭窗体
calcwindow.Close()
