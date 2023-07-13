rm -rf output/
rm -rf layer/
rm layer.zip
mkdir output
#pip3 install -r ./requirements.txt --target=output
#pip3 install stockstats --target=output
#pip3 install scipy --target=output
cd output
#rm -rf panda*/
#rm -rf nump*/
#rm -rf panda*/
#rm -rf nump*/
#rm -rf scipy*/
#rm -rf boto*/
#rm -rf stockstat*
#rm stockstats.py
cp ../history.py .
cp ../market_scanner.py .
cp ../backtest.py .
cp ../indicators.py .
cp ../notification.py .
cp ../functions.py .
#zip stockstats.zip stockstats.py
zip -r ../layer.zip .
cd ..
