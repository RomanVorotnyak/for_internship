import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylammpsmpi import LammpsLibrary
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.optimize import curve_fit


# константы для преобразования из системы Леннарда-Джонса в СИ
epsilon = 1.65e-21  # Дж
sigma = 3.4e-10  # м
mass = 6.63e-26  # кг
k_B = 1.38e-23  # Дж/К

# константа газовая для СИ
R = 8.314  # Дж/(моль·К)

# загрузка движка lammps
lmp = LammpsLibrary(cores=4)

input_file = "input_script.in"

# инпут скрипт с описанием термодинамической системы
input_script = """
units lj
atom_style atomic
lattice fcc 0.8442
region box block 0 10 0 10 0 10
create_box 1 box
create_atoms 1 box
mass 1 1.0
velocity all create 1.44 87287
pair_style lj/cut 2.5
pair_coeff 1 1 1.0 1.0 2.5
fix 1 all nvt temp 1.0 1.0 0.1
thermo 100
thermo_style custom step temp press
thermo_modify flush yes
run 10000
"""

with open(input_file, 'w') as f:
    f.write(input_script)

lmp.file(input_file)

log_file = "log.lammps"

# извлекаем данные из лог файла
def extract_thermo_data(log_file):
    steps = []
    temps = []
    pressures = []

    with open(log_file, 'r') as file:
        lines = file.readlines()
        read_data = False

        for line in lines:
            if "Step" in line and "Temp" in line and "Press" in line:
                read_data = True
                continue

            if read_data:
                data = line.split()
                if len(data) < 3:  # проверка на случай если меньше данных чем надо (но у нас все ок)
                    continue
                try:
                    steps.append(int(data[0]))
                    temps.append(float(data[1]))
                    pressures.append(float(data[2]))
                except ValueError:
                    # вдруг че фигню понаписалась, то скипаем
                    continue

    return np.array(steps[2:]), np.array(temps[2:]), np.array(pressures[2:])

steps, temperatures_lj, pressures_lj = extract_thermo_data(log_file)

# Преобразование температуры и давления из системы LJ в СИ
temperatures_si = temperatures_lj * epsilon / k_B
pressures_si = pressures_lj * epsilon / (sigma**3)

volume_lj = 10**3  # Пример значения объема в LJ
number_of_particles = 4000  # Количество частиц
volume_si = volume_lj * sigma**3  # Объем в СИ

# Расчет zeta(P, T) в СИ
zeta_si = pressures_si * volume_si / (number_of_particles * temperatures_si * k_B)


# 2D-гистограмма для zeta от температуры
plt.figure(figsize=(8, 6))
plt.hist2d(temperatures_si, zeta_si, bins=50, cmap='viridis')
plt.colorbar(label='Density')
plt.xlabel('Temperature (K)')
plt.ylabel('Zeta (SI units)')
plt.title('2D Histogram of Zeta vs Temperature')
plt.savefig('zeta_vs_temperature_hist.png')
plt.show()

# 2D-гистограмма для zeta от давления
plt.figure(figsize=(8, 6))
plt.hist2d(pressures_si, zeta_si, bins=50, cmap='viridis')
plt.colorbar(label='Density')
plt.xlabel('Pressure (Pa)')
plt.ylabel('Zeta (SI units)')
plt.title('2D Histogram of Zeta vs Pressure')
plt.savefig('zeta_vs_pressure_hist.png')
plt.show()

# Scatter plot для zeta от температуры и давления
plt.figure(figsize=(8, 6))
plt.scatter(temperatures_si, zeta_si, label='Zeta vs Temperature', alpha=0.5, edgecolors='w', s=50)
plt.scatter(pressures_si, zeta_si, label='Zeta vs Pressure', alpha=0.5, edgecolors='r', s=50)
plt.xlabel('Temperature (K) / Pressure (Pa)')
plt.ylabel('Zeta (SI units)')
plt.title('Scatter Plot of Zeta vs Temperature and Pressure')
plt.legend()
plt.savefig('zeta_vs_temp_pressure_scatter.png')
plt.show()

# Параметры Ван-дер-Ваальса, рассчитанные на основе параметров Леннарда-Джонса
a_vdw_theory = 1.42e-1  # В м^6 Па/моль^2
b_vdw_theory = 9.46e-5  # В м^3/моль

# Количество молекул (частиц), участвующих в симуляции, переведем в количество молей
n_moles = number_of_particles / 6.022e23  # Число молей

# Мольный объем для каждого давления и температуры в системе СИ
V_m = volume_si / n_moles  # мольный объем в м^3/моль

# Теоретическая функция для расчета zeta по уравнению Ван-дер-Ваальса
def zeta_vdw_theory(P, T, a, b):
    Vm = V_m
    return (P * Vm) / (R * T) * ((Vm - b) / Vm - a / (R * T * Vm))

# Вычислим zeta по уравнению Ван-дер-Ваальса для каждого давления и температуры
zeta_vdw_theory_values = zeta_vdw_theory(pressures_si, temperatures_si, a_vdw_theory, b_vdw_theory)

# Полиномиальная регрессия для zeta от температуры
poly_features = PolynomialFeatures(degree=2)
X_temp_poly = poly_features.fit_transform(temperatures_si.reshape(-1, 1))
model_temp = LinearRegression()
model_temp.fit(X_temp_poly, zeta_si)

# Предсказание значений для температуры
temp_range_si = np.linspace(min(temperatures_si), max(temperatures_si), 100).reshape(-1, 1)
zeta_temp_pred_si = model_temp.predict(poly_features.transform(temp_range_si))

# Полиномиальная регрессия для zeta от давления
X_press_poly = poly_features.fit_transform(pressures_si.reshape(-1, 1))
model_press = LinearRegression()
model_press.fit(X_press_poly, zeta_si)

# Предсказание значений для давления
press_range_si = np.linspace(min(pressures_si), max(pressures_si), 100).reshape(-1, 1)
zeta_press_pred_si = model_press.predict(poly_features.transform(press_range_si))

# Сравнение Zeta vs Temperature с теоретическими значениями
plt.figure(figsize=(8, 6))
plt.scatter(temperatures_si, zeta_si, label='Experimental Zeta vs Temperature', alpha=0.5, edgecolors='w', s=50)
plt.plot(temp_range_si, zeta_temp_pred_si, color='red', label='Polynomial fit')
plt.plot(temperatures_si, zeta_vdw_theory_values, label='Van der Waals Theory', linestyle='--', color='blue')  # Добавляем теоретическую кривую
plt.xlabel('Temperature (K)')
plt.ylabel('Zeta (SI units)')
plt.title('Comparison of Zeta vs Temperature with Experimental and Theoretical Values')
plt.legend()
plt.show()

# Сравнение Zeta vs Pressure с теоретическими значениями
plt.figure(figsize=(8, 6))
plt.scatter(pressures_si, zeta_si, label='Experimental Zeta vs Pressure', alpha=0.5, edgecolors='w', s=50)
plt.plot(press_range_si, zeta_press_pred_si, color='red', label='Polynomial fit')
plt.plot(pressures_si, zeta_vdw_theory_values, label='Van der Waals Theory', linestyle='--', color='blue')  # Добавляем теоретическую кривую
plt.xlabel('Pressure (Pa)')
plt.ylabel('Zeta (SI units)')
plt.title('Comparison of Zeta vs Pressure with Experimental and Theoretical Values')
plt.legend()
plt.show()