import xarray as xr
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score,mean_squared_error
from sklearn.preprocessing import StandardScaler

ds = xr.open_dataset("MERRA-2.nc4")

co = ds["CO"].mean(dim=["time","lat","lon"]).values
aird = ds["AIRDENS"].mean(dim=["time","lat","lon"]).values
ps = ds["PS"].mean(dim=["time","lat","lon"]).values
delp = ds["DELP"].mean(dim=["time","lat","lon"]).values
o3 = ds["O3"].mean(dim=["time","lat","lon"]).values

df = pd.DataFrame({
    "CO": co,
    "AIRDENS": aird,
    "PS": ps,
    "DELP": delp,
    "O3": o3
}).dropna()

X = df[["CO"]]
y = df["O3"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Score R²:", r2_score(y_test, y_pred))
print(f"{mean_squared_error(y_test,y_pred)}%")
print("Coefficients:", model.coef_)
