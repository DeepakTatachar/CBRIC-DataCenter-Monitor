# CBRIC-DataCenter-Monitor

Requirements
------------
- python 3.6 or higher
- paramiko
- numpy
```
pip install -r requirements.txt
```

How to run?
-----------
```python
python main.py
```
- Runs on Windows, Linux and MacOS
- Runs outside of ecn servers, yes you can run this on you personal PC/Mac
- If you username is different from the one on the machine, use
```
python main.py --u 'username on CBRIC machines'
``` 

When you run, you will be prompted for a username (may pick this up automatically) and password. Then when it runs you should see usage reports like

![alt text][logo]

[logo]: https://github.com/DeepakTatachar/CBRIC-DataCenter-Monitor/blob/master/images/App.JPG
