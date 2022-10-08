# HealthTAG FHIR Transformer

ตัวแปลงไฟล์ XML ของ CSOP และไฟล์ CSV ของ 43 แฟ้ม ให้อยู่ในรูปของ FHIR Resource

# การใช้งาน
## Local installation
### Requirements
1. Python 3.10
2. pipenv [ดาวน์โหลดและติดตั้ง](https://pipenv.pypa.io/en/latest/)
3. FHIR Server (ex HAPI FHIR Server)

### การติดตั้ง
1. Clone repository นี้ลงไปยังเครื่องคอมพิวเตอร์
2. `pipenv install`

### การใช้งาน
1. ให้ `cd` ไปยัง fhir-transformer ก่อน (เช่นให้ command prompt อยุ่ที่ `C:\Users\Sutti\source\repos\healthtag-organization\fhir-transformer`) จากนั้นเปิด Virtual environment โดยใช้ `pipenv shell`
```commandline
cd C:\Users\Sutti\source\repos\healthtag-organization\fhir-transformer
pipenv shell
```
2. นำ Folder ที่ข้างในมีไฟล์ที่ต้องการแปลง ใส่ลงใน Folder ชื่อ `workingdir` เช่น
```
--workingdir
    |-- 2022_10_06
        |-- billdispXXXXXXXXX.txt
        |-- billtransXXXXXXXX.txt
```
จากนั้นสามารถรันได้สองวิธีคือ **คอยดู Folder** กับ **ระบุ Folder**
```commandline
❯ python -m fhir_transformer -h                            
usage: __main__.py [-h] [--watch] [--type {csop,43folders}] [--name FOLDER_NAME]

HealthTAG FHIR Transformer

options:
  -h, --help              show this help message and exit
  --watch                 Use watch mode. Please read the manual to understand how to use this mode
  --type {csop,43folders} Specify processing type.
  --name FOLDER_NAME      Specify name of folder inside "workingdir" folder
```
#### แบบระบุ Folder
ให้ใส่ parameter เช่น `python -m fhir_transformer --type csop --name 2022_10_06` จากนั้นโปรแกรมจะทำตามคำสั่ง

#### แบบคอยดู
ให้รัน `python -m fhir_transformer --watch` จะขึ้น
```commandline
❯ python -m fhir_transformer --watch               
**********************************
* HealthTAG FHIR Transformer 2.2 *
*        8 Octorber 2022         *
*         healthtag.io           *
*      support@healthtag.io      *
**********************************
Checking on workingdir folder for any work
Finish checking and running work
Watching workingdir folder for any changes
```
จากนั้นให้สร้าง Folder งานที่จะให้โปรแกรมทำใน `workingdir` เพิ่มแล้วเอาไฟลืใส่ด้านบน จากนั้นใน Folder งานนั้น ให้สร้างไฟล์เปล่าๆ ชื่อ `csop` หรือ `43folders` เพื่อให้โปรแกรมเริ่มต้นทำงาน
```
--workingdir
    |-- 2022_10_06
    |-- 2022_10_08
        |-- billdispXXXXXXXXX.txt
        |-- billtransXXXXXXXX.txt
        |-- csop
```
3. เมื่อทำงานเสร็จใน Folder นั้นจะเกิดไฟล์ชื่อ `result.json` เพื่อให้สามารถดูผลลัพธ์การส่ง FHIR Resource ไปยัง FHIR Server `log.txt` เพื่อดู stdout และ `done` หรือ `error`
### Docker image
[https://hub.docker.com/repository/docker/healthtag/fhir-transformer](https://hub.docker.com/repository/docker/healthtag/fhir-transformer)
