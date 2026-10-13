while read file; do
    echo $file
    combine -M AsymptoticLimits $file --run blind --rMin 0 --rMax 0.1 --rAbsAcc 0.00005
    name="${file#*_}"
    name="${name%.*}"
    mv higgsCombineTest.AsymptoticLimits.mH120.root "${name}AsymptoticLimits.root"
done < datacardList.txt
