rm -rf output/
rm -rf layer/
rm layer.zip
rm -rf function/
rm function.zip
mkdir output
#pip3 install -r ./requirements.txt --target=output
pushd output
#rm -rf panda*/
#rm -rf nump*/
#rm -rf scipy*/
#rm -rf boto*/
#rm -rf stockstat*
cp ../lambda_function.py .
#cp -r ../data/ ./data/
#cp -r ../configs/ ./configs/
zip -r ../function.zip .
