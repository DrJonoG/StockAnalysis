
class Overview:
    def __init__(self):
        self.df = pd.DataFrame(columns=[
            "Sym",
            "Float",
            "Earnings_Date",
            "Avg_Price",
            "ATR",
            "Avg_Vol",
            "Data_Points"
        ])

    def Create(self):
        pass

    def FromFile(self, file, source):
        for filename in glob.glob(source + "*.csv"):
            df = pd.read_csv(filename)
            # Create overview of symbol
            sym = Path(filename).name.split("_")[0]
            avg_price = df["close"].mean()
            atr = df["high"].max() - df["low"].min()
            avg_vol = df["volume"].mean()
            data_points = len(df)
            # append
            self.df = self.df.append({"Sym": sym, "Float": "0", "Earnings_Date": "01/01/1999", "Avg_Price": avg_price,"ATR": atr,"Avg_Vol": avg_vol, "Data_Points": data_points}, ignore_index=True)

        self.df.to_csv(file, index=True)

    def Run(self, folder):
        if not os.path.exists(folder + "_overview.csv"):
            self.Create(folder + "_overview.csv", source=folder)
        overview = pd.read_csv(folder + "_overview.csv")
        return overview
