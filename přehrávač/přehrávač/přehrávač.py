
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import fnmatch
import os
from pygame import mixer
from mutagen.mp3 import MP3

mixer.init () #inicializace

# Hlavní okno
root = tk.Tk()
root.title("Prehravac hudby")
root.geometry("800x700")

#PROSTŘEDÍ
#vytvoření canvas
canvas = tk.Canvas (root)
canvas.config(bg='pink')
canvas.pack(fill=tk.BOTH, expand=True)

def vyber_slozku():
    """
        Vyskočí okénko pro výběr složky, ze které se budou skladby přehrávat
    """
    vybrana_slozka = filedialog.askdirectory(title="Vyberte složku s hudbou")
    if vybrana_slozka:
        return vybrana_slozka
    else:
        return None  #po zavření okna vrátí none
    

#vložení hudby
#rootpath= r"C:\Tmp\Music"
rootpath = vyber_slozku()
if not rootpath:
    print("Složka nebyla vybrána. Program se ukončí.")
    exit()
#vybrání pouze mp3
pattern="*.mp3"
#seznam skladem
playlist=[]
#index přehrávané skladby
index_skladby=0
#délka aktuální skladby
delka_skladby=0
paused=False
current_song = None

#zobrazení
listBox = tk.Listbox(canvas, fg="pink", bg="white", width=100, font=('ds-digital', 14))
listBox.pack(padx=15, pady=15)
#procházení složky
for root_dir, dirs, files in os.walk(rootpath) : 
      for filename in fnmatch.filter(files, pattern):
           listBox.insert( 'end', filename )
           
#zajištění, že okno bude viditelné
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)



#funkce načtení skladem ze složky
def nacti_playlist():
    """
        Načte vybranou složku do playlistu
    """
    global playlist
    for root, dirs, files in os.walk(rootpath):
        for filename in fnmatch.filter(files, pattern):
            playlist.append(os.path.join(root, filename))
            

#FUNGOVÁNÍ TLAČÍTEK
def ovladani_prehravani():
    """
        Ovládá přeehrávání hudby- spustí skladbu, pozastaví a pokračuje v přehrávání
    """
    global delka_skladby, paused  #delka skladby + stav paused (jestli je skladba pozastavena)
    try:
        #jestlije tlačítko ve stavu play a přehraávání není pozastaveno
        if play_stop_button["text"] == "►" and not paused:           
            selected_song = listBox.get("anchor") #zístá vybranou skladbu
            if not selected_song:  # Pokud není vybraná, vybere první
                listBox.select_set(0)
                selected_song = listBox.get(0)
            
            #načte a přehraje skladbu
            mixer.music.load(os.path.join(rootpath, selected_song))
            delka_skladby = zjisti_delku_skladby(os.path.join(rootpath, selected_song))
            mixer.music.play()
            paused=False #není pozastaveno
            play_stop_button["text"] = "■"  #změní text tlačítka na "Stop"
            Label.config(text=selected_song)  #zobrazí název skladby
            prubeh_casovace()  # Spustí časovač
            
            #když je tlačitko ve stavu stop
        elif play_stop_button["text"]=="■":
            mixer.music.pause()
            paused= True
            play_stop_button["text"] = "►"  #tlačítko zpět na "Play"
        
         # když je skladba pozastavená a tlačítko je ve stavu "Play"
        elif play_stop_button["text"] == "►" and paused:
            mixer.music.unpause()  # Pokračuje v přehrávání
            paused = False  # Skladba již není pozastavená
            play_stop_button["text"] = "■"  # Změní tlačítko na "Stop"
            
            cas_label.config(text="00:00 / 00:00")  #resetuje text časovače
    except Exception as e:
        print(f"Chyba při přehrávání/stavění skladby: {e}")

        



#tlaticko pro preskoceni na na dalsi skladbu
def hrej_dalsi():
    """
        Po zmáčknutí přeskočí na další skladbu od přehrávané nebo označené skladby,
        když je na poslední skladbě, tak skočí zpátky na první
    """
    global paused, delka_skladby, current_song
    try:
        if uzivatelsky_playlist:  #když existuje uživatelský playlist
            index = uzivatelsky_playlist.index(current_song) if current_song in uzivatelsky_playlist else -1
            dalsi_index = (index + 1) % len(uzivatelsky_playlist)
            vybrana_skladba = uzivatelsky_playlist[dalsi_index]
        else:  #jinak normálně přehrává dál z hlavního seznamu
            skladba = listBox.curselection()
            if not skladba:
                return
            dalsi_index = (skladba[0] + 1) % listBox.size()
            vybrana_skladba = listBox.get(dalsi_index)

        #načtení a přehrání skladby
        mixer.music.load(os.path.join(rootpath, vybrana_skladba))
        delka_skladby = zjisti_delku_skladby(os.path.join(rootpath, vybrana_skladba))
        mixer.music.play()
        current_song = vybrana_skladba
        play_stop_button["text"] = "■"
        Label.config(text=vybrana_skladba)
        prubeh_casovace()

        #aktualizace výběru v příslušném seznamu
        if uzivatelsky_playlist:
            uziv_playlist_listbox.select_clear(0, 'end')
            uziv_playlist_listbox.select_set(dalsi_index)
        else:
            listBox.select_clear(0, 'end')
            listBox.activate(dalsi_index)
            listBox.select_set(dalsi_index)

    except Exception as e:
        print(f"Chyba při přehrávání další skladby: {e}")


#tlacitko pro preskoceni na minulou skladbu
def hrej_minulou():
    """
        Přeskočí o jednu skladbu v zad od přehrávané nebo označené skladby,
        když je na první skadbě, tak skočí na posledí
    """
    try:
        #získání aktuálního výběru
        skladba = listBox.curselection()
        if not skladba:
            return  #pokud není žádná skladba vybrána tak vrací

        #kontrolujee, jestli je aktuální skladba první v seznamu
        if skladba[0] == 0:
            minula_skladba = listBox.size() - 1  # Vybere poslední skladbu
        else:
            minula_skladba = skladba[0] - 1  # Vybere předchozí skladbu

        #získání názvu a cesty skladby
        minskl_jmeno = listBox.get(minula_skladba)
        cesta_k_skladbe = os.path.join(rootpath, minskl_jmeno)

        #zobrazí název skladby
        print(minskl_jmeno)
        Label.config(text=minskl_jmeno)

        #načtení a přehrání skladby
        mixer.music.load(cesta_k_skladbe)
        global delka_skladby
        delka_skladby = zjisti_delku_skladby(cesta_k_skladbe)

        #nastavení časovače
        casovac["maximum"] = delka_skladby
        mixer.music.play()

        #spustí časovač
        prubeh_casovace()

        #aktualizace výběru v seznamu
        listBox.select_clear(0, 'end')
        listBox.activate(minula_skladba)
        listBox.select_set(minula_skladba)

    except Exception as e:
        print(f"Chyba při přehrávání minulé skladby: {e}")


        
#ovládání hlasitosti
def nastav_hlasitost(value):
    """
        Ovládání hlasitosti, zesilování/zeslabování
    """
    hlasitost=float(value) / 100 #hodnoty 0.0-1.0
    mixer.music.set_volume(hlasitost)
    
#ukazovatel času přehrávání
def prubeh_casovace():
    """
        Funkce pro fungování a průběh časovače/progressbaru
        Zjistí délku skladby, přepočítá, nastaví hodnoty a kontroluje jestli skladba hraje, po skončení hraje další
    """
    try:
        global delka_skladby
        current_time=mixer.music.get_pos()/1000 #pro aktuální pozici v sekundaách
        if current_time < 0:  #pokud není skladba načtena, použít 0
            current_time = 0
       
        aktual_minuty=int(current_time // 60)
        aktual_sekundy=int(current_time % 60)
        total_minuty=int(delka_skladby // 60)
        total_sekundy=int(delka_skladby % 60)
        
        #aktualizace casovace a casoveho/textoveho labelu
        casovac["value"]=current_time
        casovac["maximum"]=delka_skladby
        cas_label.config(
            text=f"{aktual_minuty:02}:{aktual_sekundy:02}/{total_minuty:02}:{total_sekundy:02}"
            )
        
        #kontrola jestli skaldba stále hraje
        if current_time < delka_skladby:
            root.after(500, prubeh_casovace)
        else:
            hrej_dalsi()
            
        if current_time >= delka_skladby:
            hrej_dalsi()
            
    except Exception as e:
        print(f"Chyba v časovači: {e}")
      
             
  #získání délky skladby
def zjisti_delku_skladby(cesta_k_skladbe):
    """
        Zjistí délku skladby
    """
    try:
        
        zvuk = MP3(cesta_k_skladbe)
       
        return zvuk.info.length
             
    except Exception as e:
        print(f"Chyba při získávání délky skladby: {e}")
        return 0


#TLAČÍTKA
#vytvoření Label pro display
Label = tk.Label(canvas,text=' ',bg='pink', fg='black',font=('ds-digital,18'))
#vložení label na canvas
Label.pack(pady=15)

#vytvoření frame pro organizaci - horizontální zobrazení, pro tlačítka atd
top = tk.Frame (canvas, bg="pink")
top.pack(padx=10,pady=5,anchor='center')
#vytvoření tlačítka
zpetButton=tk.Button(canvas,text="«",bg='pink',font=('ds-digital',35),borderwidth=0,command=hrej_minulou)
#jeho zobrazení
zpetButton.pack(pady=15, in_=top,side='left')


#tlačítko "Play" a "Stop"
play_stop_button = tk.Button(
    canvas, text="►", bg="pink", font=('ds-digital', 25), borderwidth=0, command=ovladani_prehravani
)
play_stop_button.pack(pady=15, in_=top, side='left')

#tlačítko dopředu
vpredButton=tk.Button(canvas,text="»",bg='pink',font=('ds-digital',35),borderwidth=0,command=hrej_dalsi)
vpredButton.pack(pady=15, in_=top,side='left')

#posuvník pro hlasitost
hlasitost_label=ttk.Label(canvas,text="Hlasitost:",background="pink",font=('ds-digital',15),borderwidth=0) #posuvník pro ohládání hlasitosti
hlasitost_label.pack()

hl_posuvnik=ttk.Scale(
    canvas,
    #root,
    from_=0, #min hlasitost
    to=100, #max hlasitost
    orient="horizontal",
    command=nastav_hlasitost
    )
hl_posuvnik.set(50) #výchozí nastavení na 50%
hl_posuvnik.pack(pady=10)

#casovac
casovac=ttk.Progressbar(canvas, orient="horizontal", length=300, mode="determinate")
casovac.pack(pady=20)

#label pro casovac
cas_label = tk.Label(canvas, text="00:00 / 00:00", bg="pink", fg="black", font=("ds-digital", 15))
cas_label.pack(pady=5)

# Uživatelský playlist
uzivatelsky_playlist = []

#pridání skladby do uživatelského playlistu
def pridej_do_playlistu():
    """
        Vloží označenou skladbu z původního playlistu do listboxu uživatelského playlistu
    """
    try:
        skladba = listBox.get("anchor")
        if skladba and skladba not in uzivatelsky_playlist:
            uzivatelsky_playlist.append(skladba)
            uziv_playlist_listbox.insert("end", skladba)  #aktualizuje to zobrazení
    except Exception as e:
        print(f"Chyba při přidávání skladby do playlistu: {e}")

#odebrání skladby z uživatelského playlistu
def odeber_z_playlistu():
    """ 
        Vymaže označenou skladbu z uživatelského playlistu
    """
    try:
        vybrana_skladba = uziv_playlist_listbox.get("anchor")
        if vybrana_skladba in uzivatelsky_playlist:
            uzivatelsky_playlist.remove(vybrana_skladba)
            uziv_playlist_listbox.delete("anchor")  #aktualizuje zobrazení
    except Exception as e:
        print(f"Chyba při odebírání skladby z playlistu: {e}")

#přehrání další skladby podle uživatelského playlistu

def hrej_dalsi_v_playlistu():
    """
        Přehrává další skladbu z uživatelksého playlistu když je zvolen nebo z normálního playlistu
        
        Zjistí ve kterém z playlistá se hraná skladba nachází a přehraje pak další.
        Když je poslední v seznamu, tak hraje první skladbu
    
    """
    global paused, delka_skladby, current_song
    try:
        if uzivatelsky_playlist:
            index = uzivatelsky_playlist.index(current_song) if current_song in uzivatelsky_playlist else -1
            dalsi_index = (index + 1) % len(uzivatelsky_playlist) #hraje další - poslední -len- vráti na začátek
            vybrana_skladba = uzivatelsky_playlist[dalsi_index]
        else:
            #normální přehrávání
            skladba = listBox.curselection()
            if not skladba:
                return
            dalsi_index = (skladba[0] + 1) % listBox.size()
            vybrana_skladba = listBox.get(dalsi_index)

        mixer.music.load(os.path.join(rootpath, vybrana_skladba))
        delka_skladby = zjisti_delku_skladby(os.path.join(rootpath, vybrana_skladba))
        mixer.music.play()
        current_song = vybrana_skladba
        play_stop_button["text"] = "■"
        Label.config(text=vybrana_skladba)
        prubeh_casovace()

        # Aktualizace výběru v uživatelském playlistu
        if uzivatelsky_playlist:
            uziv_playlist_listbox.select_clear(0, 'end')
            uziv_playlist_listbox.select_set(dalsi_index)
        else:
            listBox.select_clear(0, 'end')
            listBox.activate(dalsi_index)
            listBox.select_set(dalsi_index)

    except Exception as e:
        print(f"Chyba při přehrávání další skladby v playlistu: {e}")


# Vytvoření rámu pro Listbox a tlačítka vedle sebe
main_frame = tk.Frame(canvas, bg="pink")
main_frame.pack(pady=15, padx=15, fill="both", expand=True)

#levo sloup listbox
listbox_frame = tk.Frame(main_frame, bg="pink")
listbox_frame.pack(side="left", fill="both", expand=True)

#pravo, label a tlačítka
playlist_frame = tk.Frame(main_frame, bg="pink")
playlist_frame.pack(side="right", fill="both", expand=True)

uziv_playlist_label = tk.Label(listbox_frame, text="Uživatelský playlist", bg="pink", fg="black", font=("ds-digital", 15))
uziv_playlist_label.pack(pady=(0,5),padx=10)

uziv_playlist_listbox = tk.Listbox(listbox_frame, fg="pink", bg="white", width=40, font=("ds-digital", 14))
uziv_playlist_listbox.pack(padx=10, pady=(0,10), fill="both", expand=True)

#tlačítka pod uživatelským playlistem
playlist_buttons = tk.Frame(playlist_frame, bg="pink")
playlist_buttons.pack(pady=10)

pridej_button = tk.Button(
    playlist_buttons, text="Přidat do playlistu", bg="pink", font=("ds-digital", 14), command=pridej_do_playlistu
)
pridej_button.pack(side="top", pady=5, padx=10)

odeber_button = tk.Button(
    playlist_buttons, text="Odebrat z playlistu", bg="pink", font=("ds-digital", 14), command=odeber_z_playlistu
)
odeber_button.pack(side="top", pady=5, padx=10)



nacti_playlist()
# Spuštění aplikace
root.mainloop()