# Yu-Gi-Oh! Fusion helper
Given a set of card ids, it gets every fusion of the game "Yu-Gi-Oh! Forbidden Memories" (PlayStation 1). It was 
made quickly to win some duels in the game. If you want and have time, you can improve so much thing on this very 
raw script, like put all in CSV files or make a nice GUI. Have fun with retro games! :)

![Screenshot of script being running](./static/img/readme_test.png)

## Usage with Windows
Download yugioh-fusion-helper release (zip file) from:

https://github.com/ignaciora/yugioh-fusion-helper/releases/tag/v1.0

Then unzip, open a terminal ("CMD" or "PowerShell") on that folder and run the following command:

```powershell
> .\yugioh_fusion_helper.exe --list 004,214,044,395,396,267,114
```

The numbers separated by commas should be your cards IDs (from hand and field).

### Windows users advice
It is posible that the exe file will be recognize as malware by Windows Defender. It need this to be ignore in order
to execute the program. The only thing that is doing is connecting to the site "https://yugipedia.com" to get the cards
data. If you don't want to ignore the antivirus's warning you can execute the script .py with python (this requires 
python 3 installed).

The exe file in the "/dist" folder was compile using PyInstaller (https://www.pyinstaller.org/) with the following 
command:
```python
> pyinstaller --clean --onefile -c .\yugioh_fusion_helper.py
```
You can compile it by yourself if you want to be sure.

## Installation and usage with Python 3
Install Python 3.x and pip 3.
Download the source code from latest release or clone this repository. Then place yourself on that folder.
Open a terminal, move to the downloaded folder and run the following commands:

```python
> python -m venv ./env  (Optional)
> ./env/Scripts/activate  (Optional)
> python -m pip install -r requirements.txt
> python ./yugioh_fusion_helper.py --list 004,214,044,395,396,267,114
```

The numbers separated by commas should be your cards IDs (from hand and field).
