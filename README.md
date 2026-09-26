# Japan Life — Native APK Preservation Project

โปรเจกต์นี้เปลี่ยนแนวทางจากการสร้างเกมใหม่ด้วย Godot มาเป็น **การแก้ไข APK ของ Japan Life เดิมโดยตรง** เพื่อรักษาระบบ เกมเพลย์ แผนที่ กราฟิก เสียง ข้อมูล และ native engine เดิมให้มากที่สุด

## เป้าหมาย

- ใช้ APK Japan Life v1.5.12 เป็นฐาน
- ไม่สร้างเกมทดแทนจากศูนย์
- แก้ปัญหาภาษาไทยที่แสดงเป็น `□`
- ตรวจและแก้ปัญหาเด้ง/compatibility โดยเปลี่ยนเฉพาะส่วนที่จำเป็น
- รักษาไฟล์เกมเดิมและ native library `libKyotoLife.so` เป็นหลัก
- ทำทุกแพตช์ให้ตรวจสอบย้อนกลับได้ และมี automated verification
- สร้าง APK ที่ติดตั้งและทดสอบได้ผ่าน GitHub Actions

## โครงสร้าง

- `tools/inspect_japanlife.py` — ตรวจโครงสร้าง APK/native library/font pack
- `tools/patch_japanlife.py` — แพตช์แบบ byte-exact โดยมี precondition/postcondition
- `.github/workflows/native-apk-build.yml` — ดาวน์โหลด APK ต้นฉบับจาก URL ที่ผู้ใช้ระบุ, แพตช์, zipalign และ sign
- `docs/patch-plan.md` — แผน reverse engineering และรายการสิ่งที่ต้องแก้

> APK ต้นฉบับไม่ถูก commit ลง Git เพื่อหลีกเลี่ยงการเผยแพร่ตัวเกมโดยไม่จำเป็น ให้ workflow รับ APK ที่ผู้ใช้มีสิทธิ์ใช้งานผ่าน URL หรือให้ทำ local build ด้วยสคริปต์แทน

## หลักการสำคัญ

เรา **ไม่แทนที่ระบบเกมด้วยเกมใหม่** การแก้จะเริ่มจาก binary/resources เดิม และจะเปลี่ยนให้น้อยที่สุดเท่าที่จำเป็น

Apktool รองรับการถอดและประกอบ APK ใหม่ แต่โปรเจกต์นี้จะพยายามใช้การแก้ ZIP/native library โดยตรงก่อน เพื่อหลีกเลี่ยงการสร้าง resources และ manifest ใหม่โดยไม่จำเป็น.

## สถานะ

- [x] ตรวจพบ `libKyotoLife.so`
- [x] ตรวจพบ `CFontRenderer` และฟังก์ชันจัดการภาษาไทยใน native library
- [x] ตรวจพบข้อมูล glyph ภาษาไทยใน `res/raw/font.smf`
- [x] สร้าง pipeline สำหรับรักษา APK เดิมและแพตช์แบบตรวจสอบได้
- [ ] ระบุ mapping ระหว่าง Thai Unicode → font pack/texture atlas ให้ถูกต้อง
- [ ] แก้ Thai glyph rendering ให้หายเป็น `□`
- [ ] ตรวจ root cause ของ crash/compatibility
- [ ] regression-test ระบบเดิมทั้งหมด
- [ ] สร้าง release APK รุ่นใช้งานจริง

## ข้อสำคัญ

แพตช์ทดลองก่อนหน้านี้ที่เปลี่ยน fallback ของ language detection **ไม่ถือว่าเป็นคำตอบสุดท้าย** เพราะผลทดสอบยังแสดง `□`. รุ่นถัดไปจึงจะไล่ที่ font-pack selection, glyph table และ texture mapping แทนการเดาเปลี่ยนค่าแบบกว้าง ๆ
