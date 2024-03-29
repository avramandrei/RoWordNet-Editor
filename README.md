# RoWordNet-Editor

This project provieds a graphical interface for editing the Romanian WordNet. For more information about it, please read the original [paper]().

## Installation
 
The projects requires `Python>=3.5`. To install the application, run the following commands:

```
git clone https://github.com/avramandrei/RoWordNet-Editor.git
cd RoWordNet-Editor
pip install -r requirements.txt
```

## Usage 

The application was developed using the Flask framework. To start the application, simply run the following command in the project directory: 

```
flask run
```

The application can now be accesed from a browser at the IP and port specified in `.flaskenv` configuration file (default: `127.0.0.1:5000`). 

## Add user

The application comes with authentification/authorization mechanisms. By default, the application has only one user (username: `admin`, password: `admin`). To add another user, move to the project directory and run the following commands:

```
python3 add_user.py [username] [password] [role] [--firstname] [--lastname]
```

| Argument | Type | Mandatory | Description |
| --- | --- | --- | --- |
| username | str | yes | Name of the user. |
| password | str | yes | Password of the user. | 
| role | str | yes | Role of the user: `user`, `moderator` or `admin`. |
| --firstname | str | no | Firstname of the user. Default: `""`. | 
| --lastname | str | no | Lastname of the user. Default: `""`. |

## Cite

If you are using this repository, please cite the following [paper](https://academiaromana.ro/sectii2002/proceedings/doc2020-4/11-Avram_Tufis.pdf) as a thank you to the authors:

```
Avram, A.M. and Mititelu, V.B., A Customizable WordNet Editor. In Fourth International Conference Computational Linguistics in Bulgaria (p. 147).
```

or in BibTeX format:

```
@inproceedings{avramcustomizable,
  title={A Customizable WordNet Editor},
  author={Avram, Andrei-Marius and Mititelu, Verginica Barbu},
  booktitle={Fourth International Conference Computational Linguistics in Bulgaria},
  pages={147}
}
```
