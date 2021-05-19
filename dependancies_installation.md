-- FICHIER REPERTORIANT LES COMMANDES POUR L'INSTALLATION DES DEPEDANCES (utiles pour la mise en place du docker) --

# ScoresTranslation
Projet transverse

# Python3 librairies installation

## Sacrebleu
```pip3 install sacrebleu```
(see also https://pypi.org/project/sacrebleu/)

## Nist
(file from https://www.nltk.org/_modules/nltk/translate/nist_score.html)

## Rouge-score
```pip3 install rouge-score```
(see also https://pypi.org/project/rouge-score/)

## Wer
(file wer.py from https://github.com/zimengq/WER)

## Pyter
```pip3 install pyter3```
(see also https://pypi.org/project/pyter/)

## CharacTER
pip3 install python-Levenshtein
sudo apt-get install gcc-multilib g++-multilib
g++ -c -fPIC -m64 -std=c99 -lm -D_GNU_SOURCE -Wall -pedantic -fopenmp -o ed.o ed.cpp -lstdc++
g++ -m64 -shared -Wl,-soname,libED.so -o libED.so ed.o

## ntlk (for nist and meteor metrics)
```pip3 install nltk```
(see also https://pypi.org/project/nltk/)


## Fuzzy-match - installation des dépendances et compilation c++

- INSTALLER OpenNMT/Tokenizer: <br>
 installer ICU: `sudo apt-get install -y icu-devtools`<br>
`git clone https://github.com/OpenNMT/Tokenizer` puis suivre instructions dans la section Compiling de https://github.com/OpenNMT/Tokenizer : <br>
 Dans le dossier Tokenizer:<br>
`git submodule update --init`<br>
`mkdir build`<br>
`cd build`<br>
`cmake ..`<br>
`make`<br>
**et faire un** `make install`<br>
- INSTALLER Boost: `sudo apt-get install libboost-all-dev`<br>
- INSTALLER GoogleTest (pour les tests juste): <br>
`sudo apt-get install libgtest-dev`<br>
`cd /usr/src/googletest/googletest`<br>
`sudo mkdir build`<br>
`cd build`<br>
`sudo cmake ..`<br>
`sudo make`<br>
`sudo cp libgtest* /usr/lib/`<br>
`cd ..`<br>
`sudo rm -rf build`<br>
`sudo mkdir /usr/local/lib/googletest`<br>
`sudo ln -s /usr/lib/libgtest.a /usr/local/lib/googletest/libgtest.a`<br>
`sudo ln -s /usr/lib/libgtest_main.a /usr/local/lib/googletest/libgtest_main.a`<br>

(d'apres https://gist.github.com/Cartexius/4c437c084d6e388288201aadf9c8cdd5)<br>

- Suite à l'échange que nous avons eu sur https://stackoverflow.com/questions/66917612/how-to-provide-custom-librairy-locations-with-cmake-variables-compiling-systran?noredirect=1#comment118298287_66917612 , il faut modifier le fichier CMakeLists.txt à la racine de fuzzy-match-master:<br>
==> remplacer la ligne: <br>
`find_library(OPENNMT_TOKENIZER_LIB OpenNMTTokenizer REQUIRED HINTS ${OPENNMT_TOKENIZER_ROOT}/lib)`<br>
par:<br>
`find_library(OPENNMT_TOKENIZER_LIB OpenNMTTokenizer REQUIRED HINTS ${OPENNMT_TOKENIZER_ROOT}/build)`<br>
(mettre build à la place de lib car **pas de dossier lib dans Tokeniser**)<br>

- Et enfin compiler:  <br>
mkdir build<br>
cd build<br>
cmake ..<br>
make<br>

