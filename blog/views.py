import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span
from chatterbot import ChatBot
#from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from django.http import HttpResponse
from django.shortcuts import render

# Initialisation du chatbot
#bot = ChatBot('RestaurantBot')


bot = ChatBot('RestaurantBot',read_only=False,
              logic_adapters=[
                {
                    'import_path':'chatterbot.logic.BestMatch',
                    'default_response':'Sorry i dont know what that means',
                    'maximun_similary_threshold':0.95
     
     
                 }])

# Entraînement du bot avec des données d'exemple
training_data = [
    "Bonjour",
    "Bonjour, comment puis-je vous aider ?",
    "Je voudrais réserver une table",
    "Pour combien de personnes ?",
    "Pour deux personnes s'il vous plaît",
    "À quelle heure voulez-vous réserver ?",
    "Pour 19h",
    "Très bien, c'est noté. Voulez-vous un coin tranquille ou plutôt animé ?",
    "Un coin tranquille s'il vous plaît",
    "C'est noté, votre réservation est confirmée pour deux personnes à 19h dans un coin tranquille. Au revoir !",
]

trainer = ListTrainer(bot)
trainer.train(training_data)

#chatterbotcorpustrainer = ChatterBotCorpusTrainer(bot)
#chatterbotcorpustrainer.train('chatterbot.corpus.english')




# Chargement du modèle de NER de spaCy
nlp = spacy.load("fr_core_news_sm")

# Ajout de patterns pour matcher les différentes requêtes du client
matcher = Matcher(nlp.vocab)
patterns = [
    [{"LOWER": "réserver"}, {"LOWER": "une"}, {"LOWER": "table"}],
    [{"LOWER": "carte"}, {"LOWER": "des"}, {"LOWER": "plats"}],
    [{"LOWER": "cuisine"}, {"LOWER": "italienne"}],
    [{"LOWER": "cuisine"}, {"LOWER": "japonaise"}],
    [{"LOWER": "cuisine"}, {"LOWER": "française"}],
    [{"LOWER": "plat"}, {"LOWER": "italien"}],
    [{"LOWER": "plat"}, {"LOWER": "japonais"}],
    [{"LOWER": "plat"}, {"LOWER": "français"}],
]
for pattern in patterns:
    matcher.add("REQUEST", None, pattern)

# Base de connaissances des différents types de plats proposés par le restaurant
knowledge_base = {
    "italien": ["pizza", "pâtes", "risotto"],
    "français": ["coq au vin", "ratatouille", "croissants"],
    "japonais": ["sushi", "ramen", "yakitori"],
}

# Logique de réponse conditionnelle
def respond(message):
    doc = nlp(message)
    # Recherche d'une correspondance avec les patterns de requête
    matches = matcher(doc)
    if matches:
        for match_id, start, end in matches:
            if nlp.vocab.strings[match_id] == "REQUEST":
                request_type = doc[start:end].text.lower()
                # Recherche d'une entité nommée de type "cuisine"
                for ent in doc.ents:
                    if ent.label_ == "cuisine":
                        # Si on trouve une correspondance avec la base de connaissances
                        if ent.text.lower() in knowledge_base:
                            menu = ", ".join(knowledge_base[ent.text.lower()])
                            return f"Voici les plats que nous proposons en cuisine {ent.text.capitalize()} : {menu}"
                        else:
                            return f"Je suis désolé, nous ne proposons pas de cuisine {ent.text.capitalize()}."
                #


    
# Fonction pour répondre aux requêtes du client
def getResponse(request):
    if request.method == 'GET':
        userMessage = request.GET.get('userMessage')
        response = bot.get_response(userMessage)
        if response.confidence > 0.5:
            chatResponse = str(response)
        else:
            chatResponse = respond(userMessage)
        return HttpResponse(chatResponse)
    else:
        return HttpResponse('Invalid request method')




def index(request):
    return render(request, 'blog/index.html')

def specific(request):
    list = [1,2,3]
    return HttpResponse(list)