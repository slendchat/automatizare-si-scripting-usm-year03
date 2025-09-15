# Мониторинг заполнения директории

    Скрипт контролирует сколько места занимает заданная директория относительно заданного
    лимита, пишет структурирование логи и при привышении порога отправляет уведомление на почту.


Скрипт использует:
 - интерпретатор `bash`
 - парсер коротких флагов `getopts`
 - `du` для сбора информации о размере директории и субдиректорий
 - `bc` для математических операций с числами с плавающей точкой
 - `awk` для работы со строками
 - `date` для отображение даты в UTC формате в логах
 - `mail` для отправки почтовых сообщений

 Семантика параметров:
 ```bash
Usage: ./script.sh -p <path> -s <size_in_MB> [-t <threshold_percent>] [-L <path_to_log_file>] [-v]
Options:
  -p    Путь к контролируемой директории (обязателен)
  -s    Лимит размера в МБ (обязателен, целое число ≥ 1)
  -t    Порог срабатывания алерта, % (1–100; по умолчанию 80)
  -L    Путь к лог-файлу (по умолчанию /var/log/my_disk_usage.log)
  -v    Подробный вывод в stdout (дублирует INFO-сообщения)
  -h    Справка
 ```

 В случае если не были переданы параметры скрипт вызывает функцию help() для вывода инструкции по использованию
 
 Пример:
```
No arguments provided error.

Usage: ./disk_usage.sh -p <path> -s <size_in_MB> [-t <threshold_percent>] [-L <path_to_log_file>] [-v]

Options:
  -p    Path to directory
  -s    Max size in MB
  -t    Threshold in percent (default: 80)
  -L    Path to log file (default /var/log/my_disk_usage.log)
  -v    Verbose
  -h    Show help

Example:
./disk_usage.sh -p target_dir/ -s 11 -t 50 -L log_dir/ -v
```

Скрипт начинает выполнение с проверки наличия аргументов, если аргументы не заданы выводит соответствующую ошибку и help. + выходит(exit 1)
```bash
if [ $# -eq 0 ]; then
  echo "No arguments provided error."
  echo
  help
  exit 1
fi
```
 
 `$#` возвращает число аргументов и если оно равно 0, то выполняет код ниже.

 функция help просто выводит помощь
```bash
help() {
  echo "Usage: $0 -p <path> -s <size_in_MB> [-t <threshold_percent>] [-L <path_to_log_file>] [-v]"
  echo
  echo "Options:"
  echo "  -p    Path to directory"
  echo "  -s    Max size in MB"
  echo "  -t    Threshold in percent (default: 80)"
  echo "  -L    Path to log file (default /var/log/my_disk_usage.log)"
  echo "  -v    Verbose"
  echo "  -h    Show help"
  echo
  echo "Example:"
  echo "$0 -p target_dir/ -s 11 -t 50 -L log_dir/ -v"
}
```

Далее устанавливаются значения по умолчанию
```bash
threshold="80"
log_path="/var/log/my_disk_usage.log"
verbose="false"
```

Следующим шагом парсинг параметров используя короткие флаги

```bash
while getopts "p:s:t:L:hv" option; do
  case $option in
    p) dir=$OPTARG ;;
    s) maxsize=$OPTARG ;;
    t) threshold=$OPTARG ;;
    L) log_path=$OPTARG ;;
    h) 
      help
      exit;;
    v) verbose=true;;
    \?) 
      echo Invalid option, use -h to see Help
      exit 1;;
  esac
done
```
### Инициализация
Фрагмент кода `"p:s:t:L:hv"` указывает что флаги p: s: t: L: имеют значения которые в них передаются,
а :h :v не имеют значения а устанавливают определенные флаги.

В случае неверного параметра (\?) вызывается сообщение об ошибке с просьбой глянкть -h (Help) + выход из скрипта.

Происходит инициализация логов, создание директории в которой должен находиться лог.
```bash
if [ ! -e "${log_path}" ]; then       # Проверка существования лога
  log_dir=$(dirname "${log_path}")    # Вытащить путь лог файла
  if [ ! -d "${log_dir}" ]; then      # Если не существует директория
    mkdir -p "${log_dir}"             # Создать директорию рекурсивно со всеми субдиректориями
  fi
fi
```

### Валидация параметров
Следующим этапом следует валидация всех параметров на соответсвие необходимым требованиям.
Используются операторы `-z` - проверка на пустую строку, `-d` - проверка существования каталога.
Также `!` в качестве 'not', и `-lt` - меньше(для чисел), `-gt` больше(для чисел), `-le` - меньше либо равно(для чисел).

Например:
```bash
if ! [[ "${maxsize}" =~ ^[0-9]+$ ]]; then # Проверка соответствия строки регулярному выражению
  log_err "-s must be an integer"       # Вызывается функция вывода ошибки
  help
  exit 1                                # Выход из скрипта
fi
```
- Пояснение `=~` работает только внутри `[[...]]` двойных квадратных скобок

### Вывод

Для вывода используется две функции log_info и log_err. Их задача состоит в том что вывод ошибок соблюдает определенный паттерн который необходимо прописывать для каждой ошибки поэтому этот код был вынесен в отдельную функцию.
Также дополнительная возможность для скрипта это вывод напрямую в консоль информации при выполнении скрипта при помощи параметра -v который задается при запуске.

```bash
log_info() {
  echo "ts=$(date --utc +%FT%TZ) level=INFO $1" >> "${log_path}" 
  if [ "${verbose}" = true ]; then
    echo "$1" 
  fi
}
log_err() {
  echo "ts=$(date --utc +%FT%TZ) level=ERROR message=\"$1\"" >> "${log_path}" 
  >&2 echo "[ERROR] $1" 
}
```

Уточнения:
По умолчанию логи пишутся в файл "/var/log/my_disk_usage.log", что можно заменить параметром -L
Ошибки выводятся не в стандартный поток вывода, а в стандартный поток ошибок.
Ошибки выводятся в консоль по умолчанию, в то время как дополнительная информация выводится только если ключ -v был передан скрипту.


### Логика

```bash
dir_size=$(du -sb "${dir}" | awk '{print $1}')
```
- `du -sb "${dir}"` - считает размер директории в байтах (-s = summary, -b = в байтах).
- `awk '{print $1}'` - берёт первое поле (размер)
- `dir_size` - содержит размер директории в байтах.

```bash
dir_sizemb=$(echo "scale=2; ${dir_size}/1024/1024" | bc)
```
- Делим байты на `1024*1024`, чтобы получить размер в MB.
- `scale=2` - округляем до двух знаков после запятой.

```bash
maxsizeb=$(( maxsize*1024*1024 ))
```
- Переводим размер из байтов в MB.

```bash
usage=$( echo "scale=2; ${dir_size}/${maxsizeb}*100" | bc )
```
- Получаем процент использования делением и умножением на 100
- округляем до 2 знаков после запятой.

```bash
if (( $(echo "${usage} >= ${threshold}" | bc -l) )); then
  log_info "${usage}% (dir usage) >= ${threshold}% (threshold)"
  send_email_alert
fi
```
- Проверка если `usage >= threshold`
- bc -l математическая проверка с плавающей точкой
- двойные круглые скобки нужны чтобы обрабатывать результат как число 0 -false 1 - true
- вызов функции отправки емейла.

```bash
send_email_alert()
{
  echo "[FIRING] Directory ${dir} exceeded threshold (${usage}% used)" \
  | mail -s "Disk usage alert" "example@example.com"
}
```
- Вызов функции с отправкой емейла через утилиту mail.

```bash
trap 'log_err "Script interrupted"; exit 1' INT TERM
```
- если скрипт получит сигнал INT или TERM то залогирует ошибку "Script interrupted".