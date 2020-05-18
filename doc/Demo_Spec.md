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

### <font color=#009900>自动化可能的项目</font>   
必要项目（最适合自动化测试的项目）：  
内检的初次测试，以及每次变更后的回归测试：  
- RRTE中各Menu项名称的Label  
- RRTE中各Parameter项名称的Label  
- RRTE中各Method项名称的Label  
- RRTE中各Menu项的层级结构  
- RRTE中Parameter和Method的排列顺序  
- RRTE中TAB项及Group项的包含范围   
- RRTE中各固定单位的Label及对应关系  
- RRTE中各Parameter项的R/W属性（R/W或ReadOnly？）  
- RRTE中各Float型Parameter项的表示格式（DISPLAY_FORMART）  
- RRTE中各可写项目的上下限值  
- RRTE中各可写Enum/BitEnum项的选择肢Label及顺序   
- DPCTT执行及报告检查  
最终获取登录用LOG时：  
- 用RRTE和DPCTT取得FCG登录用LOG文件和报告文件   

挑战项目：  
- RRTE中多国语的Label
- RRTE中动态单位表示  
- RRTE中Validity条件的表示  
- RRTE中各Float型Parameter项的写入格式（WRITE_FORMART）  
- RRTE中各可写项目的写入操作的可执行性（非DD测试范围）  
- RRTE中各可写项目与DB的一致性（可通过其它途径修改DB时）  
- FieldMate中的各种测试  

迫切需要自动化但目前无方案的项目：  
- Trex中的各种测试  
- Trex取得登录用LOG文件   

自动化无意义的项目：  
- RRTE中METHOD各对话框Label表示（依赖于实机外部输入信号）  
- Read Only的Enum/BitEnum项的选择肢Label及顺序   
- RRTE中各测量值与输入信号的一致性（非DD测试范围）  
