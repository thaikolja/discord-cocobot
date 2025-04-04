# # Copyright (C) 2025 by Kolja Nolte
# # kolja.nolte@gmail.com
# # https://gitlab.com/thaikolja/discord-cocobot
# #
# # This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# # You are free to use, share, and adapt this work for non-commercial purposes, provided that you:
# # - Give appropriate credit to the original author.
# # - Provide a link to the license.
# # - Distribute your contributions under the same license.
# #
# # For more information, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
# #
# # Author:    Kolja Nolte
# # Email:     kolja.nolte@gmail.com
# # License:   CC BY-NC-SA 4.0
# # Date:      2014-2025
# # Package:   Thailand Discord
#
# # Import the discord library for interacting with the Discord API
# import discord
# # Import the commands extension from discord.ext for creating bot commands
# from discord.ext import commands
# # Import the app_commands module from discord for creating application commands
# from discord import app_commands
# # Import the random library for generating random numbers
# import random
# # Import the asyncio library for working with asynchronous code
# import asyncio
# # Import the json library for working with JSON data
# import json
# # Import the fuzz function from fuzzywuzzy for fuzzy string matching
# from fuzzywuzzy import fuzz  # Using fuzzy matching for answer comparison
#
#
# # Define a new class called QuizCog that inherits from commands.Cog
# class QuizCog(commands.Cog):
# 	# Define the constructor method for the QuizCog class
# 	def __init__(self, bot: commands.Bot):
# 		# Initialize the bot attribute with the provided bot instance
# 		self.bot = bot
# 		# Initialize an empty dictionary to store quiz sessions
# 		self.quiz_sessions = {}
# 		# Initialize an empty list to store vocabulary items
# 		self.vocab_list = []
#
# 	# Define a new application command called quiz
# 	@app_commands.command(name="quiz", description="Take a vocabulary quiz")
# 	# Define the parameters for the quiz command
# 	@app_commands.describe(length="Number of questions in the quiz")
# 	async def quiz_command(self, interaction: discord.Interaction, length: int = 5, level: int = 1):
# 		"""
# 		Start a vocabulary quiz with the specified number of questions and difficulty level.
#
# 		Args:
# 				interaction (discord.Interaction): The interaction that triggered the command.
# 				length (int, optional): The number of questions in the quiz. Defaults to 5.
# 				level (int, optional): The difficulty level of the quiz. Defaults to 1.
# 		"""
#
# 		# Load vocabulary items based on the difficulty level
# 		vocab_file = f"./assets/data/thai-vocabulary-level-{level}.json"
# 		try:
# 			# Attempt to open the vocabulary file in read mode with UTF-8 encoding
# 			with open(vocab_file, "r", encoding="utf-8") as f:
# 				# Load the vocabulary data from the file using json.load
# 				vocab_list = json.load(f)
# 				# Store the vocabulary data in the vocab_list attribute
# 				self.vocab_list = vocab_list
# 		except FileNotFoundError:
# 			# If the file is not found, send an error message to the user
# 			await interaction.response.send_message(f"Vocabulary file '{vocab_file}' not found. Please contact the bot administrator.", ephemeral=True)
# 			# Return from the function to prevent further execution
# 			return
#
# 		# Prevent multiple active quiz sessions for the same user
# 		if interaction.user.id in self.quiz_sessions:
# 			# If the user already has an active quiz session, send an error message
# 			await interaction.response.send_message("You already have an ongoing quiz. Please finish the current quiz first.", ephemeral=True)
# 			# Return from the function to prevent further execution
# 			return
#
# 		# Select a random subset of vocabulary items
# 		questions = random.sample(vocab_list, min(length, len(vocab_list)))
#
# 		# Initialize quiz session
# 		self.quiz_sessions[interaction.user.id] = {
# 			"questions":     questions,
# 			"current_index": 0,
# 			"score":         0,
# 			"interaction":   interaction
# 		}
#
# 		# Ask the first question
# 		await self.ask_question(interaction)
#
# 	# Define a new method to ask a question in the quiz
# 	async def ask_question(self, interaction: discord.Interaction):
# 		"""
# 		Ask a question in the quiz.
#
# 		Args:
# 				interaction (discord.Interaction): The interaction that triggered the command.
# 		"""
#
# 		# Get the quiz session for the user
# 		session = self.quiz_sessions.get(interaction.user.id)
# 		if not session:
# 			# If the session is not found, return from the function
# 			return
#
# 		# Get the current question
# 		question = session["questions"][session["current_index"]]
#
# 		# First response to the user (Interaction response)
# 		if session["current_index"] == 0:
# 			# Send a message to the user with the first question
# 			await interaction.response.send_message(
# 				f"### Well, well, well, look who's here! Ready to add some new Thai words to your coconut brain? I'll give you {len(session['questions'])} words in **Thai** along with "
# 				f"their "
# 				f"transliteration, "
# 				f"you'll respond in **English**. Deal? (Ssssh: For every word, there are *three* alternatively accepted words, so \"don't tink too mut naaa)\"\n"
# 				f"But be careful, August Engelhardt is watching. If you score `0`, he'll instruct you to crack open a :coconut: with your bare teeth! Oh, and by the way: **You've got "
# 				f"`30` seconds per word**—starting **now!**\n\n"
# 				f"**First word**: What does `{question['thai']}` (`{question['transliteration']}`) mean in English?"
# 			)
# 		else:
# 			# Follow-up responses after the first message
# 			await interaction.followup.send(
# 				f"**Word #{session['current_index'] + 1}**: What's `{question['thai']}` (`{question['transliteration']}`) in English?"
# 			)
#
# 		# Wait for the user's response
# 		try:
# 			# Wait for a message from the user with a timeout of 30 seconds
# 			msg = await self.bot.wait_for(
# 				"message",
# 				timeout=30.0,
# 				check=lambda m: m.author == interaction.user and isinstance(m.channel, discord.abc.GuildChannel)
# 			)
# 		except asyncio.TimeoutError:
# 			# If the user times out, send a message with the correct answer
# 			await interaction.followup.send(f"Time's up! Fell asleep under my beautiful coconut tree, huh? The correct answer was: `{question['english']}`.")
# 			# Move on to the next question
# 			await self.next_question(interaction)
# 			# Return from the function to prevent further execution
# 			return
#
# 		# Clean the user's answer (strip quotes, extra spaces)
# 		user_answer = msg.content.strip().lower().replace("'", "").replace('"', "")  # Removing quotes
# 		correct_answers = [answer.lower().replace("'", "").replace('"', "") for answer in question.get("accepted", [question["english"]])]
#
# 		# Include the "english" word in the correct answers list
# 		correct_answers.append(question["english"].lower())
#
# 		success_string = f" {question['right']}. **`1` more for you!**"
# 		error_string = f" {question['wrong']} Right answer: **{question['english']}** (Nope, no for you for this one, don't even ask!)"
#
# 		# Use the success and error messages from the JSON
# 		success_message = question.get("success_message", success_string)
# 		error_message = question.get("error_message", error_string)
#
# 		# Check for exact match first
# 		if user_answer in correct_answers:
# 			# If the user's answer is correct, increment their score
# 			session["score"] += 1
# 			# Send a success message to the user
# 			await interaction.followup.send(success_message.format(score=session["score"]))
# 		else:
# 			# Use fuzzy matching as a fallback
# 			for correct_answer in correct_answers:
# 				# Calculate the similarity ratio between the user's answer and the correct answer
# 				ratio = fuzz.ratio(user_answer, correct_answer)
# 				if ratio > 80:  # Increased threshold to 80
# 					# If the ratio is above the threshold, increment the user's score
# 					session["score"] += 1
# 					# Send a success message to the user
# 					await interaction.followup.send(success_message.format(score=session["score"]))
# 					# Break out of the loop
# 					break
# 			else:
# 				# If the user's answer is not correct, send an error message
# 				await interaction.followup.send(error_message.format(correct_answer=question["english"], score=session["score"]))
#
# 		# Move on to the next question
# 		await self.next_question(interaction)
#
# 	# Define a new method to move on to the next question
# 	async def next_question(self, interaction: discord.Interaction):
# 		"""
# 		Move on to the next question in the quiz.
#
# 		Args:
# 				interaction (discord.Interaction): The interaction that triggered the command.
# 		"""
#
# 		# Get the quiz session for the user
# 		session = self.quiz_sessions.get(interaction.user.id)
# 		if not session:
# 			# If the session is not found, return from the function
# 			return
#
# 		# Increment the current index
# 		session["current_index"] += 1
# 		if session["current_index"] < len(session["questions"]):
# 			# If there are more questions, ask the next question
# 			await self.ask_question(interaction)
# 		else:
# 			# If there are no more questions, end the quiz
# 			await interaction.followup.send(f"** Yay, you made it! I hereby award you your deserved `{session['score']}`. Keep 'em safe, otherwise *someone* might steal it.**")
# 			# Remove the quiz session from the dictionary
# 			del self.quiz_sessions[interaction.user.id]
#
# 	# New quit function to allow users to quit the quiz
# 	@app_commands.command(name="quit_quiz", description="Quit the current quiz")
# 	async def quit_quiz(self, interaction: discord.Interaction):
# 		"""
# 		Quit the current quiz.
#
# 		This command allows users to quit the quiz they are currently participating in.
# 		It will display their final score and remove their session from the quiz sessions dictionary.
#
# 		Args:
# 				interaction (discord.Interaction): The interaction object that triggered this command.
#
# 		Returns:
# 				None
# 		"""
# 		# Retrieve the quiz session for the user who triggered this command
# 		session = self.quiz_sessions.get(interaction.user.id)
#
# 		# Check if a quiz session exists for the user
# 		if session:
# 			# Retrieve the user's current score from the session data
# 			score = session["score"]
# 			# Remove the user's quiz session from the quiz sessions dictionary
# 			del self.quiz_sessions[interaction.user.id]
# 			# Send a message to the user with their final score
# 			await interaction.response.send_message(f"You've quit the quiz. Your score was {score} 🥥.", ephemeral=True)
# 		else:
# 			# If no quiz session exists for the user, send a message indicating they are not in a quiz
# 			await interaction.response.send_message("You are not currently in a quiz.", ephemeral=True)
#
#
# # Define a setup function to add the QuizCog to the bot
# async def setup(bot: commands.Bot):
# 	"""
# 	Add the QuizCog to the bot.
#
# 	This function is used to add the QuizCog to the bot, making its commands and functionality available.
#
# 	Args:
# 			bot (commands.Bot): The bot object to add the QuizCog to.
#
# 	Returns:
# 			None
# 	"""
# 	# Add the QuizCog to the bot
# 	await bot.add_cog(QuizCog(bot))
