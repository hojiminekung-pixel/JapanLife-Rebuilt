# World Life Character Outfit Library

The character system keeps the original Master as the gameplay base. This library defines distinct black-duck outfits for tutorial/dialog roles so future chapters can add new presenters without reusing the same costume.

## Current role set

1. **นายกเทศมนตรี** — `mayor` — ฮัปปิญี่ปุ่นสีน้ำเงินเข้ม ขอบทอง ลายซากุระ — ตัวละครแนะนำหลัก
2. **รองนายกเทศมนตรี** — `deputy_mayor` — สูททางการสีเข้ม เนกไท — บทแนะนำ/งานบริหาร
3. **งานเทศกาล** — `festival` — ยูกาตะเทศกาลญี่ปุ่น พร้อมดอกไม้ — เทศกาลเมือง
4. **ไกด์ท่องเที่ยว** — `tour_guide` — เสื้อท่องเที่ยว แว่น และหมวกฟาง — แนะนำสถานที่
5. **นักสำรวจ** — `explorer` — ชุดสำรวจ กระเป๋าเป้ และกล้อง — ภารกิจสำรวจ
6. **เชฟ** — `chef` — ชุดเชฟสีขาวและหมวกเชฟ — ร้านอาหาร/ภารกิจอาหาร
7. **พนักงานออฟฟิศ** — `office` — ชุดทำงานสำนักงาน — ระบบงานทั่วไป
8. **วิศวกร/ก่อสร้าง** — `engineer` — เสื้อสะท้อนแสง หมวกนิรภัย — ก่อสร้าง/ปรับปรุงเมือง
9. **ตำรวจ/รักษาความปลอดภัย** — `security` — เครื่องแบบตำรวจเมือง — ความปลอดภัย/ภารกิจเมือง
10. **แพทย์/สาธารณสุข** — `doctor` — เสื้อกาวน์แพทย์ — โรงพยาบาล/สุขภาพ
11. **ครู** — `teacher` — ชุดครูพร้อมแฟ้ม — การศึกษา
12. **อีเวนต์พิเศษ** — `special_event` — ชุดคอสเพลย์สีเขียวธีมอีเวนต์ — กิจกรรมจำกัดเวลา
13. **งานแต่งงาน** — `wedding` — ชุดพิธีแต่งงาน — พิธี/อีเวนต์พิเศษ
14. **งานเลี้ยง/ปาร์ตี้** — `party` — ชุดปาร์ตี้และเครื่องประดับ — งานฉลอง
15. **นินจา** — `ninja` — ชุดนินจาสีเข้ม — ภารกิจลับ
16. **ฤดูหนาว** — `winter` — เสื้อกันหนาวและอุปกรณ์ฤดูหนาว — กิจกรรมฤดูหนาว
17. **งานประเพณี** — `tradition` — ชุดเทศกาลญี่ปุ่นพร้อมโคมไฟ — เทศกาลท้องถิ่น
18. **อวกาศ** — `astronaut` — ชุดนักบินอวกาศ — อีเวนต์ธีมอวกาศ
19. **สตรีท** — `street` — ชุดสตรีทและหูฟัง — กิจกรรมวัยรุ่น/เมือง
20. **อนาคต** — `future` — ชุดไซเบอร์แห่งอนาคต — อีเวนต์/เนื้อเรื่องอนาคต

## Implementation rule

1. Do not replace the original player/staff slot blindly.
2. First recover the native character/NPC resource reference and animation path.
3. Preserve the existing font, map, building, packed-texture and save systems.
4. Add one role at a time and validate startup before gameplay testing.
5. Keep this library as the design source for future tutorial chapters.
