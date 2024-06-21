
import subprocess
import json
import os
import sys

cookies_header = "snize-recommendation=3b0gtqsibb;_cmp_a=%7B%22purposes%22%3A%7B%22p%22%3Afalse%2C%22a%22%3Afalse%2C%22m%22%3Afalse%2C%22t%22%3Atrue%7D%2C%22display_banner%22%3Afalse%2C%22sale_of_data_region%22%3Afalse%7D;_tracking_consent=%7B%22con%22%3A%7B%22CMP%22%3A%7B%22a%22%3A%220%22%2C%22m%22%3A%220%22%2C%22p%22%3A%220%22%2C%22s%22%3A%22%22%7D%7D%2C%22v%22%3A%222.1%22%2C%22region%22%3A%22DE%22%2C%22reg%22%3A%22GDPR%22%7D;localization=IT;countryAT=IT;ly-lang-selected=en;_ga_S86TPCYKCW=GS1.1.1718627906.1.1.1718628236.60.0.0;_shopify_essential=:AZAmOR9nAAH_KzpycGsKgmAWJvkgExDF_C--BefXp_ZdF1bEb0_W_nSGtKBiajA58AMbUuEVgscf919PyghkfNrbA5KlsmGScSyxpQ:;cart=fcf7af51f84d01b9c82df61df70a0b93;cart_sig=d0096ff8a7b6d1b2c33a41ebd134b1db;cart_ts=1718810169;cookieconsent_preferences_disabled=functionality,analytics,marketing;gender_redirect=lang=&country=&gpref=woman;keep_alive=24f0a117-dae5-474a-a636-143225b2a6a3;secure_customer_sig=c07c0d07e24fe02c821286dd7bf34abb"


data_json = json.dumps(cookies_header)
python_executable = sys.executable
env = os.environ.copy()
command = [python_executable, 'main.py', data_json]
process = subprocess.Popen(
    command,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
