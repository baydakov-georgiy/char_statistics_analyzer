# Подсчет количества символов в файлах с определнными расширениями
![image results](./assets/table_of_results.png)
Программа подсчитывает количество символов в файлах с определнными расширениями и выдает статистику в формате `csv`

## Установка
```sh
git clone https://github.com/baydakov-georgiy/char_statistics_analyzer.git
cd ./char_statistics_analyzer
```

## Использование
```sh
python char_statistics_analyzer.py <директория> -e <расширения> [-o <выходной_файл.csv>]
```

**Пример №1**

Собирает статистику по символов для файлов в директории `/path/to/files` с расширениями `.txt`, `.c`, `.cpp` и сохраняет её в файл `my_stats.csv`
```sh
python char_statistics_analyzer.py /path/to/files -e .txt .c .cpp -o my_stats.csv
```
