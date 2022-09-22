rm upload.zip
rm -r upload/
rm -r download/

mkdir -p download/bin
curl -L https://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip -o download/chromedriver.zip
curl -L https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-55/stable-headless-chromium-amazonlinux-2017-03.zip -o download/headless-chromium.zip
unzip download/chromedriver.zip -d download/bin
unzip download/headless-chromium.zip -d download/bin

mkdir upload
cp -r download/bin upload/bin
ls -l upload/bin
chmod 777 upload/bin/chromedriver
chmod 777 upload/bin/headless-chromium
cp lambda_function.py upload/
cp sbi-spreadsheet-332705-4dfb114d3549.json upload/bin
ls -l upload/bin
pip install -r pip.txt -t upload/
pip3 install -r pip3.txt -t upload/
cd upload/
zip -r ../upload.zip --exclude=__pycache__/* .
cd ../

rm -r upload/
rm -r download/