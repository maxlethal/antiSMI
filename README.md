# antiSMI

Всего три скрипта: 
1) сборщик и обработчик информации ‘get_batch_into_pickle’: собирает новости из телеграмм-каналов СМИ (через микро-сервисы), парсит json, чистит от мусора, классифицирует новости, делают их саммаризацию и заголовок, записывает в словарь, который сохраняет в datadframe, сохраняемый в формате pkl.
2) модуль обновления базы данных ‘update_db’ 
3) основной файл запуска ‘main’, который занимается оркестрацией предыдущих двух скриптов с помощью библиотеки планировщика и асинхронизации

![изображение](https://user-images.githubusercontent.com/67437106/177498597-b62cb620-f1c7-4a99-9553-42c78951dcd0.png)

В папке размещены юпитеровские ноутбуки, которые использовал для экспериментов и имплементации подходов. 
Наверное там смотреть бессмысленно: много бессистемного кода, ключевой перешёл в питоновские скрипты.


NB! Нет файла requirments.txt, не загружены модели, веса и т.д. (всё очень тяжелое), не готовил удаленный репозиторий для сколь-нибудь удобного внешнего пользования: работаю в локальном.
