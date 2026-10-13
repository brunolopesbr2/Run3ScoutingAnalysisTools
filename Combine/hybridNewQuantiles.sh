for q in 0.025 0.160 0.500 0.840 0.975; do
  combine -M HybridNew --LHCmode LHC-limits datacard_Stop-M400-cT0p1.root -m 125 \
    -D higgsCombine_asimov.GenerateOnly.mH125.123456.root:toys/toy_asimov \
    --readHybridResults --grid=grid_Stop400CT0p1.root --expectedFromGrid $q \
    -n .MStop400.quant$q --plot=cls_MStop400_q$q.png
done
