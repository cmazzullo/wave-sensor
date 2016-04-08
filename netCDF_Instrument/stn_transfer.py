import os
import shutil


path_base = "C:\\Users\\chogg\\Documents\\GitHub\\wave-sensor\\netCDF_Instrument"
dest_base = "C:\\Users\\chogg\\Documents\\GitHub\\wavelab-stn"
# skip_count = len(path_base) 


ignore_files = ['.gitignore', 'README.md', 'stn_transfer.py', '__init__.py', 'wind_script.py','master.py']
 
for root, sub_folders, files in os.walk(dest_base):
    for file_in_root in files:
         
        if  root.find('.git') == -1:
            if file_in_root not in ignore_files:
                 
                try:
                    os.remove(''.join([root,'\\',file_in_root]))
                except:
                    print(''.join([root,'\\',file_in_root]),'\n ','file not found')


#copy the files over
directories = ['', '\\netCDF_Utils', '\\tools']
file_types = ['.py','.pyx','.pyd','.c']
for root, sub_folders, files in os.walk(path_base):
    for file_in_root in files:
         
        format_path = root.replace(path_base,'')
        if  format_path in directories:
            index = file_in_root.rfind('.')
            if file_in_root[index:] in file_types and file_in_root not in ignore_files \
                and file_in_root.find('gui') == -1:
                shutil.copy(''.join([root,'\\',file_in_root]),
                       ''.join([dest_base,format_path,'\\',file_in_root]))

        