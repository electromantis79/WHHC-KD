copy "C:\Users\cgunter\Google Drive\Sphinx\Bone\dist\UI_Simulator.exe" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator" /Y

copy "C:\Users\cgunter\Google Drive\Sphinx\Bone\defaultConfig" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator" /Y

copy "C:\Users\cgunter\Google Drive\Sphinx\Bone\gameDefaultSettings" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator" /Y

copy "C:\Users\cgunter\Google Drive\Sphinx\Bone\gameUserSettings" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator" /Y

copy "C:\Users\cgunter\Google Drive\Sphinx\Bone\segmentTimerDefaultSettings" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator" /Y

copy "C:\Users\cgunter\Google Drive\Sphinx\Bone\segmentTimerUserSettings" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator" /Y

copy "C:\Users\cgunter\Google Drive\Sphinx\Bone\userConfig" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator" /Y

robocopy "C:\Users\cgunter\Google Drive\Sphinx\Bone\Spreadsheets" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator\Spreadsheets" /e

robocopy "C:\Users\cgunter\Google Drive\Sphinx\Bone\Serial" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator\Serial" /e

robocopy "C:\Users\cgunter\Google Drive\Sphinx\Bone\Graphics" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator\Graphics" /e

robocopy "C:\Users\cgunter\Google Drive\Sphinx\build\html" "\\EMWINFILESERVER\FileServer\Customer Service\Customer Service\Simulator\html" /e

exit