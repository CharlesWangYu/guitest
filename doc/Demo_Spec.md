## <font color=#009900>自动化测试Demo工程式样</font>  

---
### <font color=#009900>背景</font>   
DD/FDI开发中，尤其是测试中，需要大量的使用到Windows GUI程序，比如各种Host程序（RRTE、FieldMate）、DPCTT等。这类GUI程序的自动化测试较命令行程序的自动化要复杂很多。  
UI Automation是Microsoft提供的一套Windows图形界面程序的操控接口，借助它可以在很大程度上实现这类程序的自动化。  
本示例工程计划借助UI Automation实现典型程序（如RRTE和DPCTT执行）在某个具体场景下的自动化执行，快速确立原型，为今后实现全面的DD/FDI测试自动化确立技术路线，并尽可能提供参考。  

### <font color=#009900>Host自动化Demo式样</font>   
- 根据配置文件取得测试输入式样、RRTE、待测FDI包或EDD文件名称，以及输出文件路径    
- 自动打开RRTE工具  
- 自动导入要测试的FDI包或EDD文件  
- 测试脚本（Excel格式）包含两个测试：  
 - 测试1个Menu下的2个Parameter项目的读取，1正确，1错误（变量名错误）   
 - 测试1个Menu下的2个Parameter项目的写入，1正确，1错误（上限值错误）  
- 生成测试结果报告（总体测试Case数、失败数、错误详细包括错误操作的脚本行数）  
- 对错误部分生成截图  

### <font color=#009900>认证申请资料获取自动化Demo式样</font>    
- 根据配置文件取得RRTE/DPCTT、输出文件路径    
- 启动RRTE获取相应LOG文件  
- 启动DPCTT获取相应报告  
- 将所有LOG文件及报告文件按照规定格式打包   
