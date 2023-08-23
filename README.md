# FMI-off-automatisation

First of all - the script ONLY runs with API Keys for 2captcha and sickw. YOU NEED BALANCE ON THE SITES.
You need to add your own keys to the .env file
The script will utilize both APIs one time while processing 1 IMEI.
1 IMEI will cost you around 0.071 USD in total so around 7 cents.
It will take around 24 - 48h to unlock your device.
The success rate is about 80% but highly depends on how old your device is - older = higher chance for success
We think Apple only checks the estimated purchase date + when the device was last synced to an iCloud account.
If the last sync is 2 years ago then it will unlock. 
Each IMEI takes around 2 minutes 


On 2captcha you can top up 3 dollars and you can process around 600 captchas.
On sickw you need to recharge around 5-50 dollars depending on how many devices you want to process.

Quick tutorial 

1. Register on 2captcha and sickw - top up your balance and get your API Keys.
2. Install python 3.11
3. Download the script folder from GitHub
4. Add them to the API keys to your .env file
5. Add your Imei list to the imei.txt file
6. Open the Folder in a cmd 
7. pip install -r requirements.txt
8. py checkbox.py
9. Enjoy


If you encounter any issues feel free to report them to me. I will take a look at it and solve it asap.
