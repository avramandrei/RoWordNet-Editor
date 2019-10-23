window.onload = function() {
    var ul = document.getElementById("create_synset_ul");
    ul.removeChild(ul.lastChild)

    if (document.getElementById("lemmaCounter").value == null)
        document.getElementById("lemmaCounter").value = Number(0);
}

function isLexicalized() {
    var checkBox = document.getElementById("nonlexicalized");
    if(checkBox.checked == true) {
        var plusLemma = document.getElementById("addLemma");
        var minusLemma = document.getElementById("removeLemma");

        plusLemma.disabled = true;
        minusLemma.disabled = true;
    } else {
        var plusLemma = document.getElementById("addLemma");
        var minusLemma = document.getElementById("removeLemma");

        plusLemma.disabled = false;
        minusLemma.disabled = false;
    }


    for(var i=0; i<lemma_counter; i++) {
        var text = document.getElementById("lemma_" + i + "_name");
        var sense = document.getElementById("lemma_" + i + "_sense");

        if (checkBox.checked == true){
            text.disabled = true;
            sense.disabled = true;
        } else {
            text.disabled = false;
            sense.disabled = false;
        }
    }
}

function addLemmaFcn() {
    var lemma_text = document.createElement("input");
    var lemma_sense = document.createElement("input");

    lemma_counter = document.getElementById("lemmaCounter").value;

    lemma_text.type = "text";
    lemma_text.classList.add("field-divided");
    lemma_text.placeholder = "name";
    lemma_text.name = "lemma_" + lemma_counter + "_name";
    lemma_text.id = "lemma_" + lemma_counter + "_name";
    lemma_text.size = 10;
    lemma_text.innerHTML += " ";

    lemma_sense.type = "text";
    lemma_sense.placeholder = "sense";
    lemma_sense.classList.add("field-divided");
    lemma_sense.name = "lemma_" + lemma_counter + "_sense";
    lemma_sense.id = "lemma_" + lemma_counter + "_sense";
    lemma_sense.size = 3;

    document.getElementById("lemmaCounter").value = Number(document.getElementById("lemmaCounter").value) + 1;

    var ul = document.getElementById("create_synset_ul");
    submit = ul.lastChild
    ul.removeChild(ul.lastChild)

    var li = document.createElement("li");
    li.appendChild(lemma_text)
    li.appendChild(lemma_sense)

    ul.appendChild(li)
    ul.appendChild(submit)
}

function removeLemmaFcn() {
    var ul = document.getElementById("create_synset_ul");
    submit = ul.removeChild(ul.lastChild)
    ul.removeChild(ul.lastChild)
    ul.appendChild(submit)

    document.getElementById("lemmaCounter").value -=1
}