package main

import (
    "encoding/csv"
    "bufio"
    "os"
    "io"
    "fmt"
)

func readData()  {
    f, _ := os.Open("../data/2016/01/EUR_USD_Week1.csv")
    r := csv.NewReader(bufio.NewReader(f))
    for {
        record, err := r.Read()
        if err == io.EOF {
            break
        }
        fmt.Println(record)
    }
}
