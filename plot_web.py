import hashlib
import io
import json
import random as ran

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from diskcache import Cache
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Initialize disk cache, common for all threads
cache = Cache("cache")

# Main function
def Egg2Fecund(N_Eggs, LarFood, AdNut, hatchability, Mc, sex_ratio, x5, SenDen, SenSize):
    #hatchability = 0.98
    x1 = 4.2
    x2 = 1
    x3 = 0.009
    x41 = 1
    x42 = 1
    #x5 = 85
    x6 = 2
    #SenDen = 0.17
    #SenSize = 1.7
    #Mc = 1.1
    N_larvae = int(round(hatchability * N_Eggs))
    SD = 0.31
    #sex_ratio = 0.5
    fecundity = []

    MeanSize = x1 * (1 - (1.0 / (x2 + np.exp(-x3 * N_larvae / LarFood))))
    larvae_size = np.random.normal(MeanSize, SD, N_larvae)
    adult_size = [x42 * j for j in larvae_size if j > Mc]
    N_Adult = int(round(x41 * len(adult_size)))
    adult_size = ran.sample(adult_size, N_Adult)
    SizeDepFecundity = AdNut * x5 * np.log(x6 + SenSize * np.array(adult_size))
    DenDepFecundity = 1 / (1 + SenDen * N_Adult)
    fecundity = SizeDepFecundity * DenDepFecundity
    for k in range(N_Adult):
        if ran.random() < sex_ratio:
            fecundity[k] = -1
    NMales = len([x for x in fecundity if x == -1])
    fecundity = list(fecundity)
    return fecundity


# Generating timeseries
def timeseries(N_Eggs, LarFood, AdNut, NoG, hatchability, Mc, sex_ratio, x5, SenDen, SenSize):
    tseries = []
    egg_tseries = []
    ext=0
    for t in range(NoG):
        egg_tseries += [N_Eggs]
        fecj = Egg2Fecund(N_Eggs, LarFood, AdNut, hatchability, Mc, sex_ratio, x5, SenDen, SenSize)
        if len(fecj) == 0 & ext == 0:
            ext = 1
        N_Eggs = sum([int(round(x)) for x in fecj if x != -1])
        tseries += [len(fecj)]
    return [egg_tseries, tseries, ext]


# Replicating timeseries
def replicates(LarFood, AdNut, hatchability, Mc, sex_ratio, x5, SenDen, SenSize, NoG, NoR, N_Eggs_init):
    all_Nt = []
    all_Nt1 = []
    all_egg_Nt = []
    all_egg_Nt1 = []
    all_egg = []
    all_adult = []
    N_Eggs = N_Eggs_init
    ext_count=0
    for rep in range(NoR):
        [N_egg, N_adult, ext]= timeseries(N_Eggs, LarFood, AdNut, NoG, hatchability, Mc, sex_ratio, x5, SenDen, SenSize)
        all_Nt += N_adult[:-1]
        all_Nt1 += N_adult[1:]
        all_egg_Nt += N_egg[:-1]
        all_egg_Nt1 += N_egg[1:]
        all_egg += [N_egg]
        all_adult += [N_adult]
        ext_count += ext
    return [all_Nt , all_Nt1, all_egg_Nt, all_egg_Nt1, all_egg, all_adult, ext_count]

# Plot data and cache it in disk cache
def plotAndCache(NoG, NoR, N_Eggs_init, LarFood, AdNut, hatchability, Mc, sex_ratio, x5, SenDen, SenSize):
    # Plot by calling replicates function
    [all_Nt , all_Nt1, all_egg_Nt, all_egg_Nt1, all_egg, all_adult, ext_count] = replicates(LarFood, AdNut, hatchability, Mc, sex_ratio, x5, SenDen, SenSize, NoG, NoR, N_Eggs_init)

    # Serialize - aka convert the data into a string format using json (javascript object notation)
    serializedData = json.dumps([NoG, NoR, N_Eggs_init, LarFood, AdNut, hatchability, Mc, sex_ratio, x5, SenDen, SenSize, all_Nt, all_Nt1, all_egg_Nt, all_egg_Nt1, all_egg, all_adult, ext_count]).encode('utf-8')

    # Generate a unique md5 hash
    cacheKey = hashlib.md5(serializedData).hexdigest()

    # Store it in the cache, give it a day to expire
    cache.set(cacheKey, serializedData, expire=60 * 60 * 24, read=True, tag='data')

    # Return the unique cache key will be used by the browser to request for Image/HTML/Excel
    return cacheKey

# Plotting
def graph(cacheKey, outputType):
    # Retrive from the cache
    storedData = cache.get(cacheKey)
    if storedData is None:
        return None

    [NoG, NoR, N_Eggs_init, LarFood, AdNut, hatchability, Mc, sex_ratio, x5, SenDen, SenSize, all_Nt, all_Nt1, all_egg_Nt, all_egg_Nt1, all_egg, all_adult, ext_count] = json.loads(storedData)

    # Display the output based on request
    if outputType.lower() == "image":

        # Image - plot using matplotlib and generate p
        fig, axs = plt.subplots(2)
        fig.tight_layout(pad=4.0)
        for i in range(len(all_egg)):
            time_axis = list(range(len(all_egg[0])))
            axs[0].plot(time_axis, all_egg[i], linewidth=1)
        axs[0].set_title("Egg timeseries")
        axs[0].set(xlabel="Generations", ylabel="Number of eggs")
        axs[0].set(xlim=(0, len(time_axis)))
        for i in range(len(all_adult)):
            time_axis = list(range(len(all_adult[0])))
            axs[1].plot(time_axis, all_adult[i], linewidth=1)
        axs[1].set_title("Adult timeseries")
        axs[1].set(xlabel="Generations", ylabel="Population size")
        axs[1].set(xlim=(0, len(time_axis)))
        plt.show()

        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return output
    else:
        df = pd.DataFrame([[LarFood], [AdNut], [hatchability], [Mc], [sex_ratio], [x5], [SenDen], [SenSize], [''], [NoG], [NoR], [N_Eggs_init]], index =["Larval food", "Adult food", "Egg hatchability", "Larval critical mass", "Proportion of males", "Size and density independent female fecundity", "Sensitivity of female-fecundity to adult density", "Sensitivity of female-fecundity to body-size", "", "No. of generations", "No. of populations", "Initial egg number"], columns = ["values"])
        df_adult = pd.DataFrame(all_adult, index = ['Pop '+str(i+1) for i in range(NoR)]).transpose()
        df_egg = pd.DataFrame(all_egg, index = ['Pop '+str(i+1) for i in range(NoR)]).transpose()

        if outputType.lower() == "html":
            return "<h3> All parameter values </h3>" \
                   + df.to_html(classes=["table table-sm", "table-bordered", "table-striped", "table-hover", "col-md-5 mb-3"]) \
                   + "<br/><h3> Egg timeseries data</h3>" \
                   + df_egg.to_html(classes=["table table-sm", "table-bordered", "text-right"]) \
                   + "<br/><h3> Adult timeseries data</h3>" \
                   + df_adult.to_html(classes=["table table-sm", "table-bordered", "text-right"])
        elif outputType.lower() == "excel":
            output_xl = io.BytesIO()
            writer = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
            writer.book.filename = output_xl

            try:
                df.to_excel(writer, sheet_name='Parameter values')
                writer.sheets['Parameter values'].set_column(0, 0, 50)

                df_egg.to_excel(writer, sheet_name='Egg timeseries')
                df_adult.to_excel(writer, sheet_name='Adult timeseries')
                writer.save()
                writer.close()
            except:
                pass

            return output_xl
