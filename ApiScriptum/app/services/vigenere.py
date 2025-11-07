"""
SERVICIOS VIGENÈRE
SCRIPTUM - Servicio de cifrado Vigenère  
Autoras: Arantxa - Wara

Este módulo proporciona funcionalidades para cifrar y descifrar texto
utilizando el algoritmo de cifrado Vigenère, incluyendo la capacidad
de guardar los resultados en archivos de texto.
"""
import os
import string


class Vigenere:
    """Clase para operaciones de cifrado y descifrado Vigenère."""

    @staticmethod
    def cifrar_vigenere(texto, clave):
        """Cifra un texto utilizando el algoritmo de Vigenère.
        
        Toma un texto plano y una clave, aplica el cifrado Vigenère y
        guarda el resultado en un archivo 'mensaje_cifrado.txt'.
        
        Args:
            texto (str): Texto a cifrar.
            clave (str): Clave para el cifrado.
            
        Returns:
            str: Texto cifrado en mayúsculas sin espacios.
        """
        txt = Vigenere.formatear_texto(texto)
        clave_ajustada = Vigenere.clave_ajustada(clave, len(txt))
        texto_cifrado = ""
        
        for i, letra in enumerate(txt):
            # Cálculo de la posición de la letra cifrada
            posicion = (ord(letra) - ord('A') + ord(clave_ajustada[i]) - ord('A')) % 26
            # Conversión de la posición a carácter
            letra_cifrada = chr(posicion + ord('A'))
            texto_cifrado += letra_cifrada
        
        # Grabar el texto cifrado completo en el archivo
        Vigenere.grabar_fichero('mensaje_cifrado.txt', texto_cifrado)
        return texto_cifrado
    
    @staticmethod
    def descifrar_vigenere(texto, clave):
        """Descifra un texto utilizando el algoritmo de Vigenère.
        
        Toma un texto cifrado y una clave, aplica el descifrado Vigenère y
        guarda el resultado en un archivo 'mensaje_descifrado.txt'.
        
        Args:
            texto (str): Texto cifrado a descifrar.
            clave (str): Clave para el descifrado.
            
        Returns:
            str: Texto original descifrado.
        """
        clave_ajustada = Vigenere.clave_ajustada(clave, len(texto))
        texto_original = ""
        
        for i, letra in enumerate(texto):
            # Cálculo de la posición de la letra original
            num_letra = ord(letra) - ord('A')
            # Convierte la letra de la clave ajustada a un número (0-25)
            num_clave = ord(clave_ajustada[i]) - ord('A')
            # Resta la clave y ajusta el rango sumando 26
            posicion = (num_letra - num_clave + 26) % 26
            # Conversión de la posición a carácter
            letra_original = chr(posicion + ord('A'))
            texto_original += letra_original

        Vigenere.grabar_fichero('mensaje_descifrado.txt', texto_original)
        return texto_original

    @staticmethod
    def clave_ajustada(clave, long):
        """Ajusta la clave repitiendo sus caracteres para alcanzar la longitud deseada.
        
        Repite la clave de forma cíclica hasta que coincida con la longitud
        del texto a procesar.
        
        Args:
            clave (str): La clave a repetir.
            long (int): Longitud objetivo para la clave.
            
        Returns:
            str: Clave repetida cíclicamente con la longitud especificada.
        """
        if clave == "":
            raise ValueError("La clave no puede estar vacía.")
        
        clave_ajustada = ""
        for i in range(long):
            # Usa módulo para obtener la posición correcta de forma cíclica
            posicion = i % len(clave)
            clave_ajustada += clave[posicion]
        return clave_ajustada

    @staticmethod
    def formatear_texto(texto):
        """Formatea el texto eliminando espacios y convirtiendo a mayúsculas.
        
        Prepara el texto para el proceso de cifrado eliminando todos los
        espacios en blanco y convirtiendo todas las letras a mayúsculas.
        
        Args:
            texto (str): Texto a formatear.
            
        Returns:
            str: Texto formateado sin espacios y en mayúsculas.
        """
        texto = texto.upper()  # 1. Convertir todo el texto a mayúsculas
        caracteres_validos = []  # 2. Crear una lista vacía para almacenar los caracteres válidos
        for c in texto:  # 3. Recorrer cada carácter del texto
            if c in string.ascii_uppercase:  # 4. Solo añadimos si está en el alfabeto inglés (A-Z)
                caracteres_validos.append(c)
        texto_depurado = "".join(caracteres_validos)
        return texto_depurado

    @staticmethod
    def grabar_fichero(nombre_fichero, contenido):
        """Guarda contenido en un archivo de texto en la carpeta data.
        
        Crea o sobrescribe un archivo en el directorio 'data/' relativo
        al directorio del proyecto Practica_Vigenere.
        
        Args:
            nombre_fichero (str): Nombre del archivo donde guardar el contenido.
            contenido (str): Contenido a escribir en el archivo.
        """
        # Obtener el directorio actual del archivo vigenere.py
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        # Ir al directorio padre (Practica_Vigenere) y luego a data
        directorio_proyecto = os.path.dirname(directorio_actual)
        # Construir la ruta completa al archivo
        ruta_archivo = os.path.join(directorio_proyecto, 'data', nombre_fichero)
        
        # Crear el directorio data si no existe
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        
        # Escribir el contenido en el archivo
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
