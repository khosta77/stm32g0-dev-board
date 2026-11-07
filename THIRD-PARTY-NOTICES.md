# Сторонние материалы

Ниже перечислены материалы, которые не являются оригинальной работой авторов
g0_dev_board и распространяются на своих условиях. Сам проект g0_dev_board
распространяется под CERN-OHL-P v2 (см. [NOTICE](NOTICE) и [LICENSE](LICENSE)).

## Библиотеки KiCad

Схемы и плата используют символы, посадочные места и 3D-модели из штатных
библиотек KiCad. Символы и посадочные места встроены в файлы `*.kicad_sch`
и `*.kicad_pcb` (так KiCad хранит их в проекте). 3D-модели в репозиторий не
входят: плата ссылается на модели из установленного KiCad
(`${KICAD10_3DMODEL_DIR}`).

| Файлы | Источник | Лицензия |
|---|---|---|
| Символы и посадочные места, встроенные в `g0_dev_board.kicad_sch`, `scheme/*.kicad_sch`, `g0_dev_board.kicad_pcb` | Штатные библиотеки KiCad, <https://www.kicad.org/libraries/> | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) с исключением KiCad для проектов |
| `g0_dev_board.kicad_sym` (символ `USB_B_Mini`, изменён под проект) | Штатная библиотека символов KiCad | CC BY-SA 4.0 с исключением KiCad |
| `g0_dev_board.pretty/Arduino_MountingHole_3.2mm.kicad_mod` | Шаблон проекта KiCad `Arduino_Uno` | CC BY-SA 4.0 с исключением KiCad |

Исключение KiCad (<https://www.kicad.org/libraries/license/>): «To the extent
that the creation of electronic designs that use 'Licensed Material' can be
considered to be 'Adapted Material', then the copyright holder waives article 3
of the license with respect to these designs and any generated files which use
data provided as part of the 'Licensed Material'.»

Благодаря этому исключению плата и производственные файлы, созданные с
использованием библиотек KiCad, распространяются под CERN-OHL-P v2. Сами
библиотечные файлы (в том числе изменённые копии из таблицы) остаются под
CC BY-SA 4.0.

## Товарные знаки

Arduino и Uno — товарные знаки их правообладателя. В проекте используются
только стандартные размеры и назначение выводов разъёмов Uno R3 для
совместимости с шилдами; плата не является продуктом Arduino и не связана
с правообладателем знака. STM32 — товарный знак STMicroelectronics.
