import nltk
from nltk.chat.util import Chat, reflections
import openai
from flask import Flask, render_template, request
import mysql.connector
import random  # Added for random response selection


# Set your OpenAI GPT-3 API key
openai.api_key = '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'

# Set up MySQL connection
db_connection = mysql.connector.connect(
    host="ec2-65-0-101-115.ap-south-1.compute.amazonaws.com",
    user="chatgpt",
    password="Stage@#$2023@",
    database="stagedb",
    port=3306
)

# Create a cursor to interact with the database
db_cursor = db_connection.cursor()

# Function to get user's name from the database
def get_user_name():
    user_id = 1  # Assuming the user ID is 1, replace it with the actual user ID
    db_cursor.execute("SELECT fname FROM users WHERE user_id = %s", (user_id,))
    result = db_cursor.fetchone()
    return result[0] if result else None

# Get user's name
user_name = get_user_name()

# Define pairs of patterns and responses
custom_pairs = [
    (r"hello|hi|Hi|hye|hii", [f"Hello, {user_name}!", f"Hi there, {user_name}!", f"How can I help you today, {user_name}?"]),
    (r"what is your name|what's your name", [f"I am a Urawarrior chatbot, {user_name}.", f"You can call me Urawarrior chatbot, {user_name}."]),
    (r"how are you", [f"I'm doing well, thank you, {user_name}!", f"I'm just a computer program, so I don't have feelings, but I'm here to assist you, {user_name}."]),
    (r"quit|exit", [f"Goodbye, {user_name}!", f"See you later, {user_name}!", f"Have a great day, {user_name}!"]),
    
    (r"feeling sad|sad|sadness", [
    f"I understand that feeling sad can be challenging, {user_name}. Remember, every storm runs out of rain, and brighter days are ahead. Focus on small steps forward and embrace the journey of healing.",
    f"Feeling sad is a temporary state, {user_name}. Find strength in your resilience. Channel your emotions into activities that bring joy and fulfillment. Every positive action contributes to your well-being.",
    f"In moments of sadness, remind yourself of your inner strength, {user_name}. Seek out activities that ignite passion and purpose. Small victories can lead to a cascade of positive change.",
    f"Sadness is a natural part of life, but it doesn't define you, {user_name}. Explore new possibilities, set achievable goals, and let each accomplishment become a stepping stone toward happiness.",
    f"Acknowledge your feelings of sadness with kindness, {user_name}. Use this time to nurture self-compassion. Surround yourself with supportive people and engage in activities that bring comfort and joy.",
    f"Every sunrise is a reminder of new beginnings, {user_name}. Embrace the opportunity to create positive changes in your life. Small, consistent efforts can lead to significant transformation.",
    f"During moments of sadness, remember that growth often comes from challenges, {user_name}. Consider this time as an opportunity for personal development and self-discovery.",
    f"Connect with the beauty of the present moment, {user_name}. Whether it's a sunset, a piece of music, or a comforting book, finding solace in the simple things can uplift your spirit.",
    f"Take a moment to reflect on your strengths and accomplishments, {user_name}. You've overcome challenges before, and you have the resilience to navigate through this period of sadness.",
    f"Your journey is unique, and so is your ability to overcome, {user_name}. Focus on self-love and self-care. Seek inspiration in the stories of those who have triumphed over adversity."
]),

    (r"feeling happy|happy|happiness|joy", [
    f"That's wonderful to hear, {user_name}! I'm glad you're feeling happy. If there's anything specific you'd like to talk about or share, I'm here to listen and chat with you. Whether it's good news, achievements, or just a general positive feeling, feel free to let me know!",
    f"That's wonderful to hear, {user_name}! I'm glad you're feeling happy. If you'd like to share more about what's making you happy or if there's anything specific you'd like to talk about, feel free to let me know. I'm here to chat and support you!",
    f"That's wonderful to hear, {user_name}! Happiness is a great state of mind. What's making you feel happy right now? If you'd like to share, I'm here to chat and celebrate those positive moments with you!",
    f"Embrace the joy in your life, {user_name}, and find happiness in the little moments that bring a smile to your face.",
    f"Cultivate gratitude, {user_name}, by appreciating the positive aspects of your life, creating a foundation for happiness.",
    f"Surround yourself with positive influences, uplifting people, and experiences, {user_name}, that bring you genuine joy.",
    f"Practice mindfulness, {user_name}, to stay present and savor the simple pleasures that contribute to your overall happiness.",
    f"Engage in activities you love, {user_name}, and that align with your passions, creating a fulfilling and joyful life.",
    f"Connect with loved ones, {user_name}, share laughter, and build meaningful relationships that contribute to your happiness.",
    f"Celebrate your achievements, {user_name}, both big and small, as they are milestones on your journey to happiness.",
    f"Foster a positive mindset, {user_name}, by focusing on solutions and possibilities, promoting a happier outlook on life.",
    f"Prioritize self-care, {user_name}, ensuring that you invest time in activities that rejuvenate your mind, body, and spirit.",
    f"Remember that happiness is a journey, not a destination, {user_name}. Enjoy the ride and create moments that make your heart smile."
]),

    (r"feeling alone|alone", [
    f"I'm sorry to hear that you're feeling alone, {user_name}. It's completely normal to feel this way at times, and reaching out for support is a positive step. If you're comfortable, consider talking to friends, family, or someone you trust about how you're feeling. If you prefer, there are also professional resources available, such as therapists or counselors, who can provide guidance and support.",
    f"I'm sorry to hear that you're feeling alone, {user_name}. It's important to remember that you're not alone in seeking support. If you feel comfortable, consider reaching out to friends, family, or someone you trust to share your feelings. Sometimes, talking to someone can provide comfort and understanding.",
    f"I'm sorry to hear that you're feeling alone, {user_name}. It's completely normal to feel this way from time to time. If you'd like to talk about what's on your mind, share your feelings, or discuss anything in particular, I'm here for you. Additionally, consider reaching out to friends, family, or a mental health professional who can provide support and understanding. You don't have to face these feelings alone."
]),

   (r"code|coding|i want to need code|program|programming", [
    f"I'm not a programmer, {user_name}. Please feel free to ask me about other topics.",
    f"While coding isn't my specialty, {user_name}, I'm here to chat about various subjects. What else would you like to talk about?",
    f"Programming isn't my forte, {user_name}, but I'm happy to discuss other topics with you. What else is on your mind?"
]),

   (r"stressed|stress", [
    f"It's okay to feel stressed, {user_name}. Here are three tips to help you overcome stress:\n1. Take a deep breath and focus on the present moment.\n2. Consider taking a short break or engaging in a relaxing activity.\n3. Reach out to someone you trust and share your feelings. You don't have to face it alone.",
    f"Feeling stressed is normal, {user_name}. Try these three strategies to alleviate stress:\n1. Practice deep breathing exercises to calm your mind.\n2. Take a break and engage in activities that bring you joy.\n3. Talk to a friend or family member about what's on your mind. Sharing can be a great relief.",
    f"Stress is a common experience, {user_name}. Here are three suggestions to help you cope:\n1. Prioritize self-care and engage in activities that promote relaxation.\n2. Break down tasks into smaller, manageable steps.\n3. Connect with others and share your feelings. Support can make a significant difference.",
    f"Remember, self-care is crucial, {user_name}. Combat stress with:\n1. Regular exercise to boost endorphins.\n2. Ensure sufficient sleep for overall well-being.\n3. Practice mindfulness or meditation for mental clarity.\n4. Express your feelings through journaling.\n5. Engage in hobbies or activities you enjoy.",
    f"Overcoming stress is a journey, {user_name}. Try these additional strategies:\n1. Establish clear boundaries for work and personal life.\n2. Break down large tasks into smaller, achievable goals.\n3. Practice positive affirmations to shift your mindset.\n4. Seek professional support if needed.\n5. Focus on gratitude and positive aspects of your life.",
    f"Stress can be challenging, but here are more techniques, {user_name}:\n1. Disconnect from technology for a short period.\n2. Surround yourself with positive influences.\n3. Create a calming environment with soothing music or aromatherapy.\n4. Set realistic expectations and avoid perfectionism.\n5. Explore activities that promote laughter and joy.",
    f"Consider these additional strategies to manage stress, {user_name}:\n1. Establish a consistent daily routine for stability.\n2. Engage in activities that bring a sense of accomplishment.\n3. Reflect on past challenges and recognize your resilience.\n4. Practice progressive muscle relaxation for physical tension release.\n5. Set aside time for activities that nourish your soul and bring you happiness.",
    f"When stressed, try these techniques for a calmer mind, {user_name}:\n1. Practice gratitude by focusing on positive aspects of your life.\n2. Engage in deep, mindful breathing exercises regularly.\n3. Allocate time for hobbies or activities that bring you joy.\n4. Connect with nature to gain a sense of tranquility.\n5. Consider seeking professional guidance if stress persists.",
    f"Navigating stress is an ongoing process, {user_name}. Additional tips include:\n1. Learn to delegate tasks and share responsibilities.\n2. Cultivate a supportive social network for emotional backing.\n3. Set realistic goals and celebrate small achievements.\n4. Experiment with relaxation techniques such as yoga or guided meditation.\n5. Prioritize a good balance between work and personal life.",
    f"Stress management is key, {user_name}. Here are more strategies to consider:\n1. Identify and challenge negative thoughts through cognitive restructuring.\n2. Establish a sleep routine to enhance overall well-being.\n3. Engage in activities that promote a sense of purpose.\n4. Embrace a healthy diet with nutritious food choices.\n5. Foster a positive mindset by focusing on solutions rather than problems."
]),

     (r"Breakups|breakup", [
    f"I understand breakups can be tough, {user_name}. Here are 10 ways to overcome bad feelings and find happiness:\n1. Allow yourself to grieve and feel the emotions without judgment.\n2. Focus on self-care, prioritize your well-being, and engage in activities that bring you joy.",
    f"Going through a breakup is challenging, {user_name}. Here are more tips to help you heal:\n3. Surround yourself with supportive friends and family who uplift and understand you.\n4. Set new personal goals to redirect your focus and build a positive future for yourself.",
    f"It's normal to feel a range of emotions after a breakup, {user_name}. Consider these suggestions:\n5. Reflect on the lessons learned from the relationship to aid personal growth.\n6. Seek professional support if needed, such as counseling or therapy, for guidance and coping strategies.",
    f"Breakups are opportunities for growth, {user_name}. Embrace these additional strategies:\n7. Rediscover your passions and hobbies that bring fulfillment.\n8. Practice mindfulness and stay present in the moment to reduce anxiety about the past or future.",
    f"Overcoming a breakup takes time, {user_name}. Here are more ways to navigate through the process:\n9. Write down your thoughts and feelings in a journal to gain clarity and closure.\n10. Forgive yourself and your ex-partner, releasing any resentment and making room for new beginnings.",
    f"Healing from a breakup is a journey, {user_name}. Consider these 10 additional suggestions:\n11. Establish healthy boundaries to protect your emotional well-being.\n12. Focus on building a positive self-image and cultivating self-love.\n13. Connect with a support group or community to share experiences and insights.",
    f"Breakups can be transformative, {user_name}. Try these strategies for a brighter outlook:\n14. Learn from the past but avoid dwelling on it; instead, concentrate on the present and future.\n15. Explore new interests or take up a new hobby to discover aspects of yourself you may not have known.",
    f"Navigating post-breakup feelings is unique for everyone, {user_name}. Here are more ways to find happiness:\n16. Allow yourself to envision and work towards new goals, creating a sense of purpose.\n17. Practice gratitude by focusing on positive aspects of your life and the opportunities for growth ahead.",
    f"Recovering from a breakup involves self-discovery, {user_name}. Keep these tips in mind:\n18. Surround yourself with positivity, whether it's through uplifting books, music, or inspiring quotes.\n19. Cultivate a strong support system and lean on friends and family for encouragement and understanding.",
    f"Embrace the process of healing and moving forward, {user_name}. Here are final suggestions:\n20. Remember that you deserve happiness and a fulfilling life. Stay open to new connections and experiences, and be kind to yourself throughout the journey."
]),

    (r"lazy|unmotivated|lack of motivation", [
    f"Start small, {user_name}. Break tasks into manageable steps and build momentum to overcome feelings of laziness.",
    f"Create a motivating environment, {user_name}, by organizing your space and surrounding yourself with positive cues.",
    f"Set realistic goals and deadlines, {user_name}, to create a sense of accomplishment, boosting motivation.",
    f"Visualize the rewards and benefits of completing tasks, {user_name}, inspiring a renewed sense of motivation.",
    f"Take short breaks, {user_name}, to refresh your mind, preventing burnout and maintaining overall motivation.",
    f"Establish a routine that includes both work and leisure, {user_name}, striking a balance for sustained motivation.",
    f"Seek inspiration from others' success stories or motivational content, {user_name}, to reignite your passion.",
    f"Identify the root cause of your lack of motivation, {user_name}, and address it, promoting a more energized mindset.",
    f"Celebrate progress and achievements, {user_name}, no matter how small, to reinforce positive motivation.",
    f"Connect with others who share similar goals or interests, {user_name}, for mutual encouragement and motivation."
]),

   (r"frustrated|frustration", [
    f"Frustration is a natural emotion, {user_name}. Take a deep breath, exhale slowly, and allow yourself a moment to regroup. Patience is the key to finding solutions.",
    f"Feeling frustrated is a sign that you care deeply about your goals, {user_name}. Break down the task at hand into smaller steps, and tackle each one systematically.",
    f"When frustration sets in, consider taking a short break, {user_name}. Step away, engage in a different activity, and return with a fresh perspective. It can make a significant difference.",
    f"Embrace the learning process, {user_name}. Mistakes and challenges are stepping stones to growth. Reflect on what you've learned, and use it to move forward more effectively.",
    f"Express your feelings of frustration through creative outlets, {user_name}. Whether it's writing, drawing, or any form of self-expression, it can help release built-up tension.",
    f"Seek a new angle, {user_name}. When faced with a frustrating situation, explore alternative approaches and solutions. Sometimes, a different perspective can lead to breakthroughs.",
    f"Share your thoughts with a trusted friend or mentor, {user_name}. External perspectives can offer insights, and talking about your frustration can be a cathartic experience.",
    f"Visualize success, {user_name}. Picture yourself overcoming challenges and achieving your goals. Focusing on a positive outcome can help shift your mindset away from frustration.",
    f"Set realistic expectations, {user_name}. Evaluate your goals and deadlines, ensuring they align with your capabilities. Adjustments may be necessary to alleviate frustration.",
    f"Remember, it's okay to ask for help, {user_name}. Reach out to colleagues, friends, or professionals who can provide guidance and support during frustrating times."
]),

    (r"terminally ill|loved one's health|coping with illness", [
    f"I'm so sorry to hear about your loved one's terminal illness, {user_name}. It's completely normal to feel a range of emotions. Take each moment as it comes and allow yourself to process your feelings.",
    f"Dealing with a loved one's terminal illness is an incredibly tough journey, {user_name}. Make sure to prioritize self-care and seek support from friends, family, or a counselor. You don't have to face this alone.",
    f"Coping with the terminal illness of a loved one is an emotional roller coaster, {user_name}. Remember to be gentle with yourself, and don't hesitate to lean on your support system for comfort and understanding.",
    f"It's okay to feel a mix of emotions, including sadness, anger, and fear, {user_name}. Take the time to communicate with your loved one and express your feelings. Open and honest conversations can be healing for both of you.",
    f"Create moments of connection and cherish the time you have together, {user_name}. Share memories, express love, and make the most of the present. These moments can become invaluable treasures.",
    f"Seek professional help if you find it challenging to cope, {user_name}. Therapists and counselors specialize in providing support during difficult times and can offer guidance on managing your emotions.",
    f"Consider joining a support group for individuals going through similar experiences, {user_name}. Sharing your thoughts and feelings with others who understand can provide a sense of community and comfort.",
    f"Take breaks when needed, {user_name}. Balancing your own well-being is crucial. Find moments of respite, engage in activities that bring you peace, and allow yourself time for emotional recovery.",
    f"If possible, involve your loved one in decisions about their care and express your willingness to support their choices, {user_name}. Maintaining open communication fosters a sense of empowerment.",
    f"Remember that everyone's journey is unique, {user_name}. There's no right or wrong way to navigate this difficult time. Trust your instincts, and allow yourself the space to grieve and find solace."
]),

]

# Create a chatbot using the custom pairs
custom_chatbot = Chat(custom_pairs, reflections)

# Function to get response from OpenAI GPT-3
def get_openai_response(user_input):
    # Replace 'your-openai-engine' with your specific GPT-3 engine name
    engine_name = 'gpt-3.5-turbo'
    
    response = openai.ChatCompletion.create(
        model=engine_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ],
        max_tokens=50  # You can adjust this based on the desired length of the response
    )
    
    return response['choices'][0]['message']['content']

# Initialize Flask app
app = Flask(__name__)

# Define route for the home page
@app.route('/')
def home():
    return render_template('chat.html', user_input="", chatbot_response="")

# Define route for handling user input and displaying chatbot response
@app.route('/chat', methods=['GET'])
def chat():
    user_input = request.args.get('user_input', '')
    
    if user_input:
        # Check if the user input matches any custom pattern
        for pattern, responses in custom_pairs:
            if nltk.re.search(pattern, user_input, flags=nltk.re.IGNORECASE):
                # Randomly select a response from the list
                response = random.choice(responses)
                break
        else:
            # If no match, get response from OpenAI
            response = get_openai_response(user_input)
    else:
        response = ""

    return render_template('chat.html', user_input=user_input, chatbot_response=response, user_name=user_name)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
