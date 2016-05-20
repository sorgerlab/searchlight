for y in `seq 0 24`; do
    for x in `seq 0 24`; do
        if [ $x -ge $y ]; then
            CMD="python compute_similarities_nienke_tcells_pieces.py $x $y"
            LOG="OUTPUT/Nienke_tcells_flow/logs/$x_$y_%J.txt" 
            echo $CMD
            bsub -q short -W 10:00 -o "$LOG" $CMD
        fi
    done
done
