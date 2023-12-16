import pandas as pd
import numpy as np
import os

def Consolidar_TXT(Directorio: str):
    '''
    Funcion que consolida todos los archivos .txt que contengan rg17 en el nombre en el directorio actual y guardarlos en un archivo consolidado.txt
    
    '''
    # consolidar todos los txt que contengan rg17 en el nombre en el directorio actual y guardarlos en un archivo consolidado.txt

    #filtrar archivos que contengan 'rg17' en el nombre respetando mayusculas y minusculas y sean .txt
    archivos = [archivo for archivo in os.listdir(Directorio) if "rg17" in archivo and archivo.endswith(".txt")]

    # ordenar archivos por nombre descendente
    archivos.sort(reverse=True)

    # concatenar archivos
    with open("Consolidado.txt", "w", encoding="latin1") as archivo_consolidado:
        for archivo in archivos:
            with open(f'{Directorio}/{archivo}' , "r", encoding="latin1") as archivo_actual:
                archivo_consolidado.write(archivo_actual.read())

def Procesar_TXT_Consolidados():
    '''
    Funcion que procesa el archivo consolidado.txt y genera un archivo consolidado procesado.csv con los datos procesados

    '''

    # Importar archivo consolidado.txt

    CertificadosIVA = pd.read_fwf("Consolidado.txt", encoding=("latin1"),
                                header=None, widths=[12,61,11,20,4], 
                                names=["CUIT" , "Denominación" , "Desde RG17" , "Hasta RG17" , "% No ret"])


    # Procesar archivo

    CertificadosIVA = CertificadosIVA[CertificadosIVA["% No ret"] == 100]
    CertificadosIVA = CertificadosIVA.drop_duplicates(subset=["CUIT" , "Desde RG17" , "Hasta RG17" , "% No ret"])
    CertificadosIVA["CUIT"] = CertificadosIVA['CUIT'].astype(np.int64)
    CertificadosIVA["Motivo RG17"] = "2" 
    CertificadosIVA["% No ret"] = CertificadosIVA["% No ret"].astype(int)
    CertificadosIVA["Desde Periodo"] = pd.to_datetime(CertificadosIVA["Desde RG17"] , format="%d/%m/%Y").dt.date.astype(str).str[0:7].str.replace("-" , "").astype(int)
    CertificadosIVA["Hasta Periodo"] = pd.to_datetime(CertificadosIVA["Hasta RG17"] , format="%d/%m/%Y").dt.date.astype(str).str[0:7].str.replace("-" , "").astype(int)
    CertificadosIVA = CertificadosIVA.sort_values(by=["CUIT","Hasta Periodo",'Desde Periodo'], ascending=[True , False, True])

    # Resetear indice
    CertificadosIVA = CertificadosIVA.reset_index(drop=True)

    # Eliminar los duplicados por 'CUIT' y 'Desde Periodo' y quedarse con el último
    CertificadosIVA = CertificadosIVA.drop_duplicates(subset=['CUIT' , 'Desde Periodo'] , keep='last')

    # Crear columna con el numero actual de veces que se repite el CUIT si el indice es menor al actual
    CertificadosIVA['Ajuste'] = CertificadosIVA['CUIT'].astype(str) + '-' + (CertificadosIVA.groupby('CUIT').cumcount() + 1).astype(str)

    # Ordenar las columnas en el siguiente orden 'Ajuste' , 'CUIT' , 'Denominación' , 'Desde RG17' , 'Hasta RG17' , '% No ret' , 'Motivo RG17' , 'Desde Periodo' , 'Hasta Periodo'
    CertificadosIVA = CertificadosIVA[['Ajuste' , 'CUIT' , 'Denominación' , 'Desde RG17' , 'Hasta RG17' , '% No ret' , 'Motivo RG17' , 'Desde Periodo' , 'Hasta Periodo']]

    #Exportar archivo
    CertificadosIVA.to_csv("Consolidado procesado.csv" , index=False , encoding="latin1" , sep="|" )

if __name__ == "__main__":
    Consolidar_TXT("Archivos")
    Procesar_TXT_Consolidados()