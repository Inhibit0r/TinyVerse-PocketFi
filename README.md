# TinyVerse

Изначально, если аккаунты еще не были добавлены в TinyVerse, первый вход осуществляется через мою реферальную ссылку. Если же вы хотите использовать свою ссылку, выполните следующие действия:

1. **Создайте публичный канал и разместите там свою реферальную ссылку, уберите предпросмотр.**

2. В `tinyVerse_main.py` найдите строку:
   ```python
   bot.send_message("https://t.me/malenkayagalaktikadao")
Pамените (https://t.me/malenkayagalaktikadao) на ссылку вашего канала.

3.	Найдите строку:
   ```python
    link = self.wait_for_element(By.CSS_SELECTOR, "a[href*='https://t.me/TVerse?startapp=galaxy']")
 ```
Замените мою реферальную ссылку https://t.me/TVerse?startapp=galaxy-0001d27add0002dfcc1f0000a93a7a на вашу.
	
4.	Если вы захотите изменить процент сбора пыли, при достижении которого происходит клейм, найдите в коде строку:
    ```python
    if howMany_StarDust >= 20:
Замените 20 на любое число от 0 до 99.

5.	После внесения изменений вы можете запускать скрипт, и он будет работать с вашими настройками.

# PocketFi

Все то же самое, если захотите загнать аккаунты по своей реферальной ссылке:

1. **Найдите строку:**
   ```python
   bot.send_message("https://t.me/poketkarmanfifi")
    ```
   Создайте канал и измените ссылку.
   	
 2.	В строке:
    ```python
    link = self.wait_for_element(By.CSS_SELECTOR, "a[href*='t.me/pocketfi_bot/mining']")
    ```
    Вместо t.me/pocketfi_bot/mining вставляете свою ссылку, и все должно спокойно работать.

  Если вы уже прогнали аккаунты, то можете закомментить следующие строки для экономии времени:
      ```    
      bot.click_what_simple_action_button()
      bot.click_start_mining_button()
      ```
