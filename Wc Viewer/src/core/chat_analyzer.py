"""
WhatsApp Chat AI Analyzer
Advanced AI-powered chat analysis with machine learning capabilities
Enhanced with Conversation Summarization, Relationship Dynamics, Topic Evolution, 
Automated Insights, and Mood Tracking
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import nltk
from textblob import TextBlob
from sentence_transformers import SentenceTransformer
import re
from collections import Counter, defaultdict
import emoji
import warnings
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
import json
import math
warnings.filterwarnings('ignore')


class ChatAIAnalyzer:
    """Enhanced AI-powered chat analyzer with advanced features"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.chat_embeddings = None
        self.is_trained = False
        self.sentiment_model = None
        self.conversation_topics = []
        
        # Enhanced AI features
        self.lda_model = None
        self.topic_evolution_data = []
        self.relationship_network = {}
        self.mood_timeline = []
        self.conversation_segments = []
        self.insights_cache = {}
        
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize AI models"""
        try:
            # Initialize sentence transformer for semantic similarity
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000, 
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Download NLTK data if not present
            self._download_nltk_data()
                
        except Exception as e:
            print(f"Error initializing AI models: {e}")
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
    
    def analyze_chat_with_progress(self, chat_data, progress_callback=None):
        """Enhanced chat analysis with new AI features and progress tracking"""
        if not chat_data:
            return {}
        
        total_steps = 10  # Updated for new features
        current_step = 0
        
        def update_progress(task_name):
            nonlocal current_step
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps, task_name)
        
        # Extract clean data
        messages = [msg['message'] for msg in chat_data if msg['message'].strip()]
        
        if not messages:
            return {'error': 'No valid messages found'}
        
        analysis = {}
        
        try:
            # Step 1: Prepare data
            update_progress("Preparing message data...")
            
            # For very large datasets, sample for some analyses
            sample_size = min(len(messages), 50000)  # Limit to 50k messages for AI analysis
            if len(messages) > sample_size:
                import random
                sampled_messages = random.sample(messages, sample_size)
                sampled_chat_data = random.sample(chat_data, sample_size)
            else:
                sampled_messages = messages
                sampled_chat_data = chat_data
            
            # Step 2: Sentiment Analysis (on sample for very large datasets)
            update_progress("Analyzing sentiment...")
            analysis['sentiments'] = self.analyze_sentiment_chunked(sampled_messages, progress_callback)
            
            # Step 3: Topic Extraction
            update_progress("Extracting topics...")
            analysis['topics'] = self.extract_topics_optimized(sampled_messages)
            
            # Step 4: Conversation Patterns (use full dataset)
            update_progress("Analyzing conversation patterns...")
            analysis['patterns'] = self.analyze_conversation_patterns(chat_data)
            
            # Step 5: User Behavior (use full dataset for accuracy)
            update_progress("Analyzing user behavior...")
            analysis['user_behavior'] = self.analyze_user_behavior(chat_data)
            
            # Step 6: NEW - Conversation Summarization
            update_progress("Generating conversation summaries...")
            analysis['summaries'] = self.generate_conversation_summaries(chat_data)
            
            # Step 7: NEW - Relationship Dynamics Analysis
            update_progress("Analyzing relationship dynamics...")
            analysis['relationship_dynamics'] = self.analyze_relationship_dynamics(chat_data)
            
            # Step 8: NEW - Topic Evolution Analysis
            update_progress("Tracking topic evolution...")
            analysis['topic_evolution'] = self.analyze_topic_evolution(chat_data)
            
            # Step 9: NEW - Mood Tracking Over Time
            update_progress("Tracking mood patterns...")
            analysis['mood_tracking'] = self.track_mood_over_time(chat_data)
            
            # Step 10: Generate embeddings and AI insights
            update_progress("Generating AI insights...")
            if len(sampled_messages) > 10000:
                # Further sample for embeddings to prevent memory issues
                embedding_sample = sampled_messages[:10000]
            else:
                embedding_sample = sampled_messages
                
            self.chat_embeddings = self.model.encode(embedding_sample, show_progress_bar=False)
            self.is_trained = True
            
            # NEW - Automated Insights Generation
            analysis['automated_insights'] = self.generate_automated_insights(analysis, chat_data)
            
            # Add metadata about sampling
            analysis['metadata'] = {
                'total_messages': len(messages),
                'analyzed_messages': len(sampled_messages),
                'embeddings_count': len(embedding_sample),
                'sampled': len(messages) > sample_size,
                'analysis_timestamp': datetime.now().isoformat(),
                'features_enabled': ['summaries', 'relationship_dynamics', 'topic_evolution', 'mood_tracking', 'automated_insights']
            }
            
        except Exception as e:
            print(f"Error in chat analysis: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def analyze_sentiment_chunked(self, messages, progress_callback=None):
        """Analyze sentiment in chunks for better performance"""
        sentiments = []
        chunk_size = 1000  # Process 1000 messages at a time
        total_chunks = (len(messages) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(messages), chunk_size):
            chunk = messages[i:i + chunk_size]
            
            for message in chunk:
                try:
                    blob = TextBlob(message)
                    sentiment = blob.sentiment.polarity
                    
                    # Categorize sentiment
                    if sentiment > 0.1:
                        category = 'positive'
                    elif sentiment < -0.1:
                        category = 'negative'
                    else:
                        category = 'neutral'
                    
                    sentiments.append({
                        'message': message[:100] + '...' if len(message) > 100 else message,
                        'sentiment': sentiment,
                        'category': category
                    })
                except Exception:
                    # Skip problematic messages
                    continue
            
            # Update progress within sentiment analysis
            if progress_callback and i % (chunk_size * 5) == 0:  # Update every 5 chunks
                chunk_progress = min(i + chunk_size, len(messages)) / len(messages)
                progress_callback(1 + chunk_progress * 0.8, 6, f"Analyzing sentiment... {i//chunk_size + 1}/{total_chunks} chunks")
        
        return sentiments
    
    def extract_topics_optimized(self, messages):
        """Optimized topic extraction for large datasets"""
        try:
            # For very large datasets, sample messages for topic analysis
            if len(messages) > 20000:
                import random
                sample_messages = random.sample(messages, 20000)
            else:
                sample_messages = messages
            
            # Clean and preprocess messages
            clean_messages = []
            for msg in sample_messages:
                # Remove very short messages and common chat words
                clean_msg = re.sub(r'\b(ok|okay|yes|no|hi|hello|bye|lol|haha|hmm)\b', '', msg.lower())
                if len(clean_msg.strip()) > 10:
                    clean_messages.append(clean_msg.strip())
            
            if len(clean_messages) < 50:
                return []
            
            # Use TF-IDF for topic extraction
            vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.7
            )
            
            tfidf_matrix = vectorizer.fit_transform(clean_messages)
            feature_names = vectorizer.get_feature_names_out()
            
            # Use KMeans clustering for topic discovery
            n_topics = min(10, max(3, len(clean_messages) // 1000))  # Dynamic topic count
            kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            topics = []
            for i in range(n_topics):
                # Get messages in this cluster
                cluster_messages = [msg for j, msg in enumerate(clean_messages) if clusters[j] == i]
                
                if not cluster_messages:
                    continue
                
                # Get top words for this cluster using cluster center
                cluster_center = kmeans.cluster_centers_[i]
                top_indices = cluster_center.argsort()[-10:][::-1]
                top_words = [feature_names[idx] for idx in top_indices if cluster_center[idx] > 0]
                
                topics.append({
                    'keywords': top_words,
                    'size': len(cluster_messages),
                    'sample_messages': cluster_messages[:3]
                })
            
            # Sort topics by size
            topics.sort(key=lambda x: x['size'], reverse=True)
            return topics
            
        except Exception as e:
            print(f"Error in topic extraction: {e}")
            return []
    
    def analyze_sentiment(self, messages):
        """Analyze sentiment of messages using TextBlob"""
        sentiments = []
        for message in messages:
            try:
                blob = TextBlob(message)
                sentiment = blob.sentiment.polarity
                sentiments.append({
                    'message': message[:50] + "..." if len(message) > 50 else message,
                    'sentiment': sentiment,
                    'category': self._categorize_sentiment(sentiment)
                })
            except Exception:
                sentiments.append({
                    'message': message[:50] + "..." if len(message) > 50 else message,
                    'sentiment': 0,
                    'category': 'neutral'
                })
        return sentiments
    
    def _categorize_sentiment(self, sentiment_score):
        """Categorize sentiment score"""
        if sentiment_score > 0.1:
            return 'positive'
        elif sentiment_score < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def extract_topics(self, messages, n_topics=5):
        """Extract main topics from conversation using K-means clustering"""
        try:
            if len(messages) < 10:
                return []
            
            # Clean and filter messages
            clean_messages = [self.clean_message(msg) for msg in messages]
            clean_messages = [msg for msg in clean_messages if len(msg.split()) > 2]
            
            if len(clean_messages) < 5:
                return []
            
            # Vectorize messages
            tfidf_matrix = self.vectorizer.fit_transform(clean_messages)
            
            # Determine optimal number of clusters
            n_clusters = min(n_topics, len(clean_messages) // 2)
            if n_clusters < 2:
                return []
                
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            # Extract topic keywords
            return self._extract_topic_keywords(kmeans, clusters, n_clusters)
            
        except Exception as e:
            print(f"Error in topic extraction: {e}")
            return []
    
    def _extract_topic_keywords(self, kmeans, clusters, n_clusters):
        """Extract keywords for each topic cluster"""
        feature_names = self.vectorizer.get_feature_names_out()
        topics = []
        
        for i in range(n_clusters):
            # Get top features for this cluster
            top_features = kmeans.cluster_centers_[i].argsort()[-10:][::-1]
            topic_words = [feature_names[j] for j in top_features]
            
            topics.append({
                'topic_id': i,
                'keywords': topic_words,
                'size': int(np.sum(clusters == i))
            })
        
        return topics
    
    def analyze_conversation_patterns(self, chat_data):
        """Analyze conversation patterns and dynamics"""
        patterns = {}
        
        try:
            df = pd.DataFrame(chat_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.day_name()
            
            # Activity patterns
            patterns['active_hours'] = df['hour'].value_counts().to_dict()
            patterns['active_days'] = df['day'].value_counts().to_dict()
            
            # Response patterns
            patterns['response_patterns'] = self.analyze_response_times(df)
            
            # Conversation starters
            patterns['conversation_starters'] = self.find_conversation_starters(df)
            
        except Exception as e:
            patterns['error'] = str(e)
        
        return patterns
    
    def analyze_user_behavior(self, chat_data):
        """Analyze individual user behavior patterns"""
        behavior = {}
        
        try:
            df = pd.DataFrame(chat_data)
            
            for sender in df['sender'].unique():
                user_messages = df[df['sender'] == sender]
                
                behavior[sender] = {
                    'total_messages': len(user_messages),
                    'avg_message_length': float(user_messages['message'].str.len().mean()),
                    'most_used_words': self.get_top_words(user_messages['message'].tolist()),
                    'emoji_usage': self.count_emojis(user_messages['message'].tolist()),
                    'activity_pattern': user_messages.groupby(user_messages['timestamp'].dt.hour).size().to_dict()
                }
                
        except Exception as e:
            behavior['error'] = str(e)
        
        return behavior
    
    def ask_question(self, question, chat_data):
        """Answer questions about the chat using AI semantic search"""
        if not self.is_trained or self.chat_embeddings is None:
            return "Please analyze the chat first before asking questions."
        
        try:
            # Encode the question
            question_embedding = self.model.encode([question])
            
            # Find similar messages
            similarities = cosine_similarity(question_embedding, self.chat_embeddings)[0]
            top_indices = similarities.argsort()[-5:][::-1]
            
            # Filter by relevance threshold
            relevant_messages = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # Relevance threshold
                    msg_data = chat_data[idx]
                    relevant_messages.append({
                        'message': msg_data['message'],
                        'sender': msg_data['sender'],
                        'timestamp': str(msg_data['timestamp']),
                        'similarity': float(similarities[idx])
                    })
            
            return self._format_ai_response(relevant_messages)
            
        except Exception as e:
            return f"Error processing question: {e}"
    
    def _format_ai_response(self, relevant_messages):
        """Format AI response from relevant messages"""
        if not relevant_messages:
            return "I couldn't find relevant messages to answer your question."
        
        response = "Based on the chat analysis, here are the most relevant messages:\n\n"
        for i, msg in enumerate(relevant_messages[:3], 1):
            message_preview = msg['message'][:100] + "..." if len(msg['message']) > 100 else msg['message']
            response += f"{i}. {msg['sender']} ({msg['timestamp']}): {message_preview}\n"
        
        return response
    
    def analyze_response_times(self, df):
        """Analyze response time patterns between users"""
        try:
            df = df.sort_values('timestamp')
            response_times = []
            
            for i in range(1, len(df)):
                if df.iloc[i]['sender'] != df.iloc[i-1]['sender']:
                    time_diff = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 60
                    if 0 < time_diff < 1440:  # Between 0 and 24 hours
                        response_times.append(time_diff)
            
            if response_times:
                return {
                    'avg_response_time': float(np.mean(response_times)),
                    'median_response_time': float(np.median(response_times)),
                    'quick_responses': len([t for t in response_times if t < 5])  # Under 5 minutes
                }
            
        except Exception as e:
            return {'error': str(e)}
        
        return {}
    
    def find_conversation_starters(self, df):
        """Find common conversation starters after long gaps"""
        try:
            starters = []
            df = df.sort_values('timestamp')
            
            for i in range(1, len(df)):
                time_gap = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 3600
                if time_gap > 2:  # More than 2 hours gap
                    starter_msg = df.iloc[i]['message'][:50].lower().strip()
                    if len(starter_msg) > 5:  # Meaningful starters
                        starters.append(starter_msg)
            
            # Count and return common starters
            starter_counts = Counter(starters)
            return dict(starter_counts.most_common(10))
            
        except Exception as e:
            return {'error': str(e)}
    
    def clean_message(self, message):
        """Clean message for processing"""
        if not message:
            return ""
        
        # Remove emojis
        message = emoji.demojize(message)
        # Remove URLs
        message = re.sub(r'http\S+', '', message)
        # Remove extra whitespace
        message = re.sub(r'\s+', ' ', message).strip()
        return message.lower()
    
    def get_top_words(self, messages, n=10):
        """Get most frequently used words"""
        try:
            all_text = ' '.join(messages).lower()
            # Extract words (3+ characters, alphabetic only)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
            
            # Filter common stopwords
            stopwords = {'the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his', 'they', 
                        'this', 'have', 'from', 'they', 'not', 'more', 'can', 'had', 'her', 'what',
                        'were', 'said', 'each', 'which', 'she', 'how', 'will', 'about', 'but'}
            
            filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
            word_counts = Counter(filtered_words)
            return dict(word_counts.most_common(n))
            
        except Exception:
            return {}
    
    def count_emojis(self, messages):
        """Count total emoji usage"""
        try:
            emoji_count = 0
            for message in messages:
                # Count Unicode emoji characters
                emoji_count += len([c for c in message if c in emoji.EMOJI_DATA])
            return emoji_count
        except Exception:
            return 0
    
    def get_summary_stats(self, analysis_results):
        """Get summary statistics from analysis results"""
        summary = {}
        
        try:
            # Sentiment summary
            if 'sentiments' in analysis_results:
                sentiments = analysis_results['sentiments']
                categories = [s['category'] for s in sentiments]
                sentiment_counts = Counter(categories)
                summary['sentiment_distribution'] = dict(sentiment_counts)
            
            # Topic summary
            if 'topics' in analysis_results:
                topics = analysis_results['topics']
                summary['total_topics'] = len(topics)
                summary['top_topic_keywords'] = topics[0]['keywords'][:5] if topics else []
            
            # User activity summary
            if 'user_behavior' in analysis_results:
                behavior = analysis_results['user_behavior']
                summary['most_active_user'] = max(behavior.items(), key=lambda x: x[1].get('total_messages', 0))[0] if behavior else None
                summary['total_participants'] = len(behavior)
            
        except Exception as e:
            summary['error'] = str(e)
        
        return summary
    
    def analyze_chat(self, chat_data):
        """Backward compatibility method - calls the progress version without callback"""
        return self.analyze_chat_with_progress(chat_data, None)

    # ==================== NEW ENHANCED AI FEATURES ====================
    
    def generate_conversation_summaries(self, chat_data: List[Dict]) -> Dict[str, Any]:
        """Generate intelligent conversation summaries using AI"""
        try:
            df = pd.DataFrame(chat_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            summaries = {
                'daily_summaries': {},
                'weekly_summaries': {},
                'conversation_segments': [],
                'key_moments': []
            }
            
            # Daily summaries
            for date, day_data in df.groupby(df['timestamp'].dt.date):
                messages = day_data['message'].tolist()
                if len(messages) < 5:  # Skip days with too few messages
                    continue
                    
                daily_summary = self._generate_text_summary(messages, max_sentences=3)
                summaries['daily_summaries'][str(date)] = {
                    'summary': daily_summary,
                    'message_count': len(messages),
                    'participants': day_data['sender'].unique().tolist(),
                    'top_keywords': self._extract_keywords(messages)[:5]
                }
            
            # Conversation segments (based on time gaps)
            segments = self._segment_conversations(df)
            for i, segment in enumerate(segments):
                segment_messages = segment['message'].tolist()
                if len(segment_messages) >= 10:  # Only summarize substantial segments
                    summaries['conversation_segments'].append({
                        'segment_id': i,
                        'start_time': str(segment['timestamp'].iloc[0]),
                        'end_time': str(segment['timestamp'].iloc[-1]),
                        'summary': self._generate_text_summary(segment_messages, max_sentences=2),
                        'participants': segment['sender'].unique().tolist(),
                        'message_count': len(segment_messages),
                        'duration_minutes': (segment['timestamp'].iloc[-1] - segment['timestamp'].iloc[0]).total_seconds() / 60
                    })
            
            # Key moments (high activity periods)
            summaries['key_moments'] = self._identify_key_moments(df)
            
            return summaries
            
        except Exception as e:
            return {'error': f"Summarization failed: {str(e)}"}
    
    def analyze_relationship_dynamics(self, chat_data: List[Dict]) -> Dict[str, Any]:
        """Analyze relationship dynamics between participants"""
        try:
            df = pd.DataFrame(chat_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            participants = df['sender'].unique()
            dynamics = {
                'interaction_matrix': {},
                'response_patterns': {},
                'communication_styles': {},
                'relationship_strength': {},
                'conversation_balance': {}
            }
            
            # Interaction matrix - who talks to whom
            for p1 in participants:
                dynamics['interaction_matrix'][p1] = {}
                p1_messages = df[df['sender'] == p1]
                
                for p2 in participants:
                    if p1 != p2:
                        # Calculate interaction frequency
                        interactions = self._calculate_interactions(df, p1, p2)
                        dynamics['interaction_matrix'][p1][p2] = interactions
            
            # Response patterns
            for participant in participants:
                dynamics['response_patterns'][participant] = self._analyze_response_pattern(df, participant)
            
            # Communication styles
            for participant in participants:
                participant_data = df[df['sender'] == participant]
                dynamics['communication_styles'][participant] = {
                    'avg_message_length': float(participant_data['message'].str.len().mean()),
                    'emoji_frequency': self._calculate_emoji_frequency(participant_data['message'].tolist()),
                    'question_frequency': self._calculate_question_frequency(participant_data['message'].tolist()),
                    'exclamation_frequency': self._calculate_exclamation_frequency(participant_data['message'].tolist()),
                    'response_speed': self._calculate_avg_response_speed(df, participant),
                    'conversation_initiation_rate': self._calculate_initiation_rate(df, participant)
                }
            
            # Relationship strength indicators
            for i, p1 in enumerate(participants):
                for p2 in participants[i+1:]:
                    strength = self._calculate_relationship_strength(df, p1, p2)
                    dynamics['relationship_strength'][f"{p1}-{p2}"] = strength
            
            # Conversation balance
            dynamics['conversation_balance'] = self._analyze_conversation_balance(df)
            
            return dynamics
            
        except Exception as e:
            return {'error': f"Relationship analysis failed: {str(e)}"}
    
    def analyze_topic_evolution(self, chat_data: List[Dict]) -> Dict[str, Any]:
        """Track how topics evolve over time"""
        try:
            df = pd.DataFrame(chat_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            evolution = {
                'topic_timeline': [],
                'trending_topics': {},
                'topic_transitions': {},
                'topic_lifecycle': {},
                'seasonal_patterns': {}
            }
            
            # Divide timeline into periods (weekly for better granularity)
            df['week'] = df['timestamp'].dt.to_period('W')
            
            # Track topics over time periods
            for week, week_data in df.groupby('week'):
                messages = week_data['message'].tolist()
                if len(messages) < 10:  # Skip weeks with too few messages
                    continue
                
                week_topics = self._extract_topics_for_period(messages)
                evolution['topic_timeline'].append({
                    'period': str(week),
                    'start_date': str(week.start_time.date()),
                    'end_date': str(week.end_time.date()),
                    'topics': week_topics,
                    'message_count': len(messages),
                    'dominant_topic': week_topics[0] if week_topics else None
                })
            
            # Identify trending topics
            evolution['trending_topics'] = self._identify_trending_topics(evolution['topic_timeline'])
            
            # Topic transitions
            evolution['topic_transitions'] = self._analyze_topic_transitions(evolution['topic_timeline'])
            
            # Topic lifecycle analysis
            evolution['topic_lifecycle'] = self._analyze_topic_lifecycle(evolution['topic_timeline'])
            
            # Seasonal patterns
            df['month'] = df['timestamp'].dt.month
            evolution['seasonal_patterns'] = self._analyze_seasonal_topic_patterns(df)
            
            return evolution
            
        except Exception as e:
            return {'error': f"Topic evolution analysis failed: {str(e)}"}
    
    def track_mood_over_time(self, chat_data: List[Dict]) -> Dict[str, Any]:
        """Track mood and emotional patterns over time"""
        try:
            df = pd.DataFrame(chat_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            mood_tracking = {
                'daily_mood': {},
                'hourly_patterns': {},
                'participant_moods': {},
                'mood_trends': {},
                'emotional_events': [],
                'mood_synchronization': {}
            }
            
            # Analyze sentiment for each message
            df['sentiment'] = df['message'].apply(self._get_message_sentiment)
            df['emotion_intensity'] = df['message'].apply(self._get_emotion_intensity)
            
            # Daily mood tracking
            for date, day_data in df.groupby(df['timestamp'].dt.date):
                daily_sentiment = day_data['sentiment'].mean()
                daily_intensity = day_data['emotion_intensity'].mean()
                
                mood_tracking['daily_mood'][str(date)] = {
                    'average_sentiment': float(daily_sentiment),
                    'emotion_intensity': float(daily_intensity),
                    'mood_category': self._categorize_mood(daily_sentiment, daily_intensity),
                    'message_count': len(day_data),
                    'participants': day_data['sender'].unique().tolist()
                }
            
            # Hourly patterns
            for hour in range(24):
                hour_data = df[df['timestamp'].dt.hour == hour]
                if len(hour_data) > 0:
                    mood_tracking['hourly_patterns'][hour] = {
                        'average_sentiment': float(hour_data['sentiment'].mean()),
                        'message_count': len(hour_data),
                        'most_common_mood': self._get_most_common_mood(hour_data)
                    }
            
            # Individual participant mood patterns
            for participant in df['sender'].unique():
                participant_data = df[df['sender'] == participant]
                mood_tracking['participant_moods'][participant] = {
                    'average_sentiment': float(participant_data['sentiment'].mean()),
                    'mood_volatility': float(participant_data['sentiment'].std()),
                    'positive_ratio': float((participant_data['sentiment'] > 0.1).sum() / len(participant_data)),
                    'negative_ratio': float((participant_data['sentiment'] < -0.1).sum() / len(participant_data)),
                    'most_positive_day': self._find_best_mood_day(participant_data, 'positive'),
                    'most_negative_day': self._find_best_mood_day(participant_data, 'negative')
                }
            
            # Mood trends over time
            mood_tracking['mood_trends'] = self._analyze_mood_trends(df)
            
            # Emotional events (significant mood changes)
            mood_tracking['emotional_events'] = self._identify_emotional_events(df)
            
            # Mood synchronization between participants
            mood_tracking['mood_synchronization'] = self._analyze_mood_synchronization(df)
            
            return mood_tracking
            
        except Exception as e:
            return {'error': f"Mood tracking failed: {str(e)}"}
    
    def generate_automated_insights(self, analysis_results: Dict, chat_data: List[Dict]) -> Dict[str, Any]:
        """Generate automated insights from all analysis results"""
        try:
            insights = {
                'key_findings': [],
                'behavioral_insights': [],
                'relationship_insights': [],
                'temporal_insights': [],
                'communication_insights': [],
                'recommendations': [],
                'anomalies': [],
                'summary_score': {}
            }
            
            # Key findings based on comprehensive analysis
            insights['key_findings'] = self._generate_key_findings(analysis_results, chat_data)
            
            # Behavioral insights
            if 'user_behavior' in analysis_results:
                insights['behavioral_insights'] = self._generate_behavioral_insights(analysis_results['user_behavior'])
            
            # Relationship insights
            if 'relationship_dynamics' in analysis_results:
                insights['relationship_insights'] = self._generate_relationship_insights(analysis_results['relationship_dynamics'])
            
            # Temporal insights
            if 'mood_tracking' in analysis_results and 'patterns' in analysis_results:
                insights['temporal_insights'] = self._generate_temporal_insights(
                    analysis_results['mood_tracking'], 
                    analysis_results['patterns']
                )
            
            # Communication insights
            if 'summaries' in analysis_results:
                insights['communication_insights'] = self._generate_communication_insights(analysis_results['summaries'])
            
            # Recommendations
            insights['recommendations'] = self._generate_recommendations(analysis_results)
            
            # Anomaly detection
            insights['anomalies'] = self._detect_anomalies(analysis_results, chat_data)
            
            # Overall summary score
            insights['summary_score'] = self._calculate_summary_score(analysis_results)
            
            return insights
            
        except Exception as e:
            return {'error': f"Automated insights generation failed: {str(e)}"}
    
    # ==================== HELPER METHODS FOR NEW FEATURES ====================
    
    def _generate_text_summary(self, messages: List[str], max_sentences: int = 3) -> str:
        """Generate a text summary from messages using extractive summarization"""
        try:
            # Combine messages into paragraphs
            text = '. '.join([msg.strip() for msg in messages if len(msg.strip()) > 10])
            
            if len(text) < 100:
                return "Brief conversation with limited content."
            
            # Simple extractive summarization
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            if len(sentences) <= max_sentences:
                return '. '.join(sentences) + '.'
            
            # Score sentences based on word frequency and position
            word_freq = Counter()
            for sentence in sentences:
                words = re.findall(r'\b\w+\b', sentence.lower())
                word_freq.update(words)
            
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                words = re.findall(r'\b\w+\b', sentence.lower())
                score = sum(word_freq[word] for word in words) / len(words) if words else 0
                # Boost early sentences slightly
                score += (len(sentences) - i) * 0.1
                sentence_scores.append((score, sentence))
            
            # Get top sentences
            top_sentences = sorted(sentence_scores, key=lambda x: x[0], reverse=True)[:max_sentences]
            top_sentences.sort(key=lambda x: sentences.index(x[1]))  # Maintain order
            
            return '. '.join([s[1] for s in top_sentences]) + '.'
            
        except Exception:
            return "Summary generation failed."
    
    def _extract_keywords(self, messages: List[str], top_k: int = 10) -> List[str]:
        """Extract keywords from messages"""
        try:
            text = ' '.join(messages).lower()
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
            
            # Filter stopwords
            stopwords = {'the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his', 'they', 
                        'this', 'have', 'from', 'not', 'more', 'can', 'had', 'her', 'what',
                        'were', 'said', 'each', 'which', 'she', 'how', 'will', 'about', 'but',
                        'just', 'like', 'get', 'now', 'see', 'know', 'think', 'good', 'time',
                        'really', 'going', 'come', 'want', 'well', 'got', 'yeah', 'okay'}
            
            filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
            word_counts = Counter(filtered_words)
            return [word for word, count in word_counts.most_common(top_k)]
            
        except Exception:
            return []
    
    def _segment_conversations(self, df: pd.DataFrame, gap_threshold_hours: int = 2) -> List[pd.DataFrame]:
        """Segment conversations based on time gaps"""
        segments = []
        current_segment_start = 0
        
        for i in range(1, len(df)):
            time_gap = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 3600
            
            if time_gap > gap_threshold_hours:
                # End current segment
                segments.append(df.iloc[current_segment_start:i])
                current_segment_start = i
        
        # Add final segment
        if current_segment_start < len(df):
            segments.append(df.iloc[current_segment_start:])
        
        return segments
    
    def _identify_key_moments(self, df: pd.DataFrame) -> List[Dict]:
        """Identify key moments in conversation"""
        key_moments = []
        
        # High activity periods
        df['hour_block'] = df['timestamp'].dt.floor('H')
        hourly_counts = df.groupby('hour_block').size()
        
        # Identify hours with unusually high activity
        mean_activity = hourly_counts.mean()
        std_activity = hourly_counts.std()
        threshold = mean_activity + 2 * std_activity
        
        high_activity_hours = hourly_counts[hourly_counts > threshold]
        
        for hour, count in high_activity_hours.items():
            hour_data = df[df['hour_block'] == hour]
            key_moments.append({
                'timestamp': str(hour),
                'type': 'high_activity',
                'message_count': int(count),
                'participants': hour_data['sender'].unique().tolist(),
                'description': f"High activity period with {count} messages"
            })
        
        return key_moments
    
    def _get_message_sentiment(self, message: str) -> float:
        """Get sentiment score for a single message"""
        try:
            blob = TextBlob(message)
            return blob.sentiment.polarity
        except Exception:
            return 0.0
    
    def _get_emotion_intensity(self, message: str) -> float:
        """Get emotion intensity score"""
        try:
            # Count emotional indicators
            exclamations = message.count('!')
            questions = message.count('?')
            caps_ratio = sum(1 for c in message if c.isupper()) / len(message) if message else 0
            emoji_count = len([c for c in message if c in emoji.EMOJI_DATA])
            
            # Emotional words
            emotional_words = ['love', 'hate', 'amazing', 'terrible', 'excited', 'sad', 'angry', 'happy']
            emotional_word_count = sum(1 for word in emotional_words if word in message.lower())
            
            intensity = (exclamations * 0.3 + questions * 0.2 + caps_ratio * 0.3 + 
                        emoji_count * 0.4 + emotional_word_count * 0.5)
            
            return min(intensity, 1.0)  # Cap at 1.0
            
        except Exception:
            return 0.0
    
    def _categorize_mood(self, sentiment: float, intensity: float) -> str:
        """Categorize mood based on sentiment and intensity"""
        if intensity < 0.2:
            return 'neutral'
        elif sentiment > 0.3:
            return 'very_positive' if intensity > 0.6 else 'positive'
        elif sentiment < -0.3:
            return 'very_negative' if intensity > 0.6 else 'negative'
        else:
            return 'mixed' if intensity > 0.4 else 'neutral'
    
    def _calculate_interactions(self, df: pd.DataFrame, p1: str, p2: str) -> Dict:
        """Calculate interaction metrics between two participants"""
        p1_messages = df[df['sender'] == p1]
        p2_messages = df[df['sender'] == p2]
        
        # Response patterns
        responses_p1_to_p2 = 0
        responses_p2_to_p1 = 0
        
        for i in range(1, len(df)):
            if df.iloc[i]['sender'] == p2 and df.iloc[i-1]['sender'] == p1:
                responses_p1_to_p2 += 1
            elif df.iloc[i]['sender'] == p1 and df.iloc[i-1]['sender'] == p2:
                responses_p2_to_p1 += 1
        
        return {
            'total_exchanges': responses_p1_to_p2 + responses_p2_to_p1,
            f'{p1}_to_{p2}_responses': responses_p1_to_p2,
            f'{p2}_to_{p1}_responses': responses_p2_to_p1,
            'interaction_ratio': responses_p1_to_p2 / max(responses_p2_to_p1, 1)
        }
    
    def _generate_key_findings(self, analysis_results: Dict, chat_data: List[Dict]) -> List[str]:
        """Generate key findings from analysis results"""
        findings = []
        
        try:
            # Message volume findings
            total_messages = len(chat_data)
            if total_messages > 10000:
                findings.append(f"Very active conversation with {total_messages:,} messages analyzed")
            
            # Participant findings
            if 'user_behavior' in analysis_results:
                participants = list(analysis_results['user_behavior'].keys())
                if len(participants) > 2:
                    findings.append(f"Group conversation with {len(participants)} participants")
                
                # Most active participant
                most_active = max(participants, key=lambda x: analysis_results['user_behavior'][x].get('total_messages', 0))
                findings.append(f"Most active participant: {most_active}")
            
            # Sentiment findings
            if 'sentiments' in analysis_results:
                sentiments = analysis_results['sentiments']
                if sentiments:
                    positive_ratio = sum(1 for s in sentiments if s['category'] == 'positive') / len(sentiments)
                    if positive_ratio > 0.6:
                        findings.append("Overall positive conversation tone")
                    elif positive_ratio < 0.3:
                        findings.append("Conversation has concerning negative sentiment")
            
            # Mood tracking findings
            if 'mood_tracking' in analysis_results:
                mood_data = analysis_results['mood_tracking']
                if 'daily_mood' in mood_data:
                    happy_days = sum(1 for day_data in mood_data['daily_mood'].values() 
                                   if day_data.get('mood_category') in ['positive', 'very_positive'])
                    total_days = len(mood_data['daily_mood'])
                    if happy_days / max(total_days, 1) > 0.7:
                        findings.append("Consistently positive mood throughout the conversation period")
            
        except Exception as e:
            findings.append(f"Error generating findings: {str(e)}")
        
        return findings[:10]  # Limit to top 10 findings
    
    def _calculate_summary_score(self, analysis_results: Dict) -> Dict[str, float]:
        """Calculate overall summary scores"""
        scores = {
            'conversation_health': 0.0,
            'engagement_level': 0.0,
            'relationship_strength': 0.0,
            'communication_quality': 0.0
        }
        
        try:
            # Calculate based on available data
            if 'sentiments' in analysis_results and analysis_results['sentiments']:
                positive_ratio = sum(1 for s in analysis_results['sentiments'] if s['category'] == 'positive') / len(analysis_results['sentiments'])
                scores['conversation_health'] = positive_ratio
            
            if 'user_behavior' in analysis_results:
                # Engagement based on message balance
                message_counts = [behavior.get('total_messages', 0) for behavior in analysis_results['user_behavior'].values()]
                if message_counts:
                    balance = 1 - (max(message_counts) - min(message_counts)) / max(sum(message_counts), 1)
                    scores['engagement_level'] = balance
            
            # Add more sophisticated scoring logic here...
            
        except Exception:
            pass
        
        return scores
    
    # Additional helper methods for comprehensive analysis
    
    def _analyze_response_pattern(self, df: pd.DataFrame, participant: str) -> Dict:
        """Analyze response patterns for a participant"""
        participant_messages = df[df['sender'] == participant]
        
        # Response times
        response_times = []
        for i in range(1, len(df)):
            if (df.iloc[i]['sender'] == participant and 
                df.iloc[i-1]['sender'] != participant):
                time_diff = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 60
                if time_diff < 60:  # Within 1 hour
                    response_times.append(time_diff)
        
        return {
            'avg_response_time_minutes': np.mean(response_times) if response_times else 0,
            'response_rate': len(response_times) / max(len(participant_messages), 1),
            'fast_responses': sum(1 for rt in response_times if rt < 5) / max(len(response_times), 1)
        }
    
    def _calculate_emoji_frequency(self, messages: List[str]) -> float:
        """Calculate emoji usage frequency"""
        total_chars = sum(len(msg) for msg in messages)
        emoji_count = sum(len([c for c in msg if c in emoji.EMOJI_DATA]) for msg in messages)
        return emoji_count / max(total_chars, 1)
    
    def _calculate_question_frequency(self, messages: List[str]) -> float:
        """Calculate question frequency"""
        question_count = sum(msg.count('?') for msg in messages)
        return question_count / max(len(messages), 1)
    
    def _calculate_exclamation_frequency(self, messages: List[str]) -> float:
        """Calculate exclamation frequency"""
        exclamation_count = sum(msg.count('!') for msg in messages)
        return exclamation_count / max(len(messages), 1)
    
    def _calculate_avg_response_speed(self, df: pd.DataFrame, participant: str) -> float:
        """Calculate average response speed in minutes"""
        response_times = []
        for i in range(1, len(df)):
            if (df.iloc[i]['sender'] == participant and 
                df.iloc[i-1]['sender'] != participant):
                time_diff = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 60
                if time_diff < 60:  # Within 1 hour
                    response_times.append(time_diff)
        
        return np.mean(response_times) if response_times else 0
    
    def _calculate_initiation_rate(self, df: pd.DataFrame, participant: str) -> float:
        """Calculate conversation initiation rate"""
        initiations = 0
        for i in range(1, len(df)):
            if (df.iloc[i]['sender'] == participant and 
                df.iloc[i-1]['sender'] != participant):
                # Check if this is after a significant gap (conversation initiation)
                time_gap = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 3600
                if time_gap > 2:  # 2+ hour gap indicates new conversation
                    initiations += 1
        
        participant_messages = len(df[df['sender'] == participant])
        return initiations / max(participant_messages, 1)
    
    def _calculate_relationship_strength(self, df: pd.DataFrame, p1: str, p2: str) -> Dict:
        """Calculate relationship strength between two participants"""
        p1_messages = df[df['sender'] == p1]
        p2_messages = df[df['sender'] == p2]
        
        # Mutual response rate
        mutual_responses = 0
        total_opportunities = 0
        
        for i in range(1, len(df)):
            if df.iloc[i-1]['sender'] == p1 and df.iloc[i]['sender'] == p2:
                mutual_responses += 1
            if df.iloc[i-1]['sender'] in [p1, p2]:
                total_opportunities += 1
        
        response_rate = mutual_responses / max(total_opportunities, 1)
        
        # Message length correlation (similar styles indicate closeness)
        p1_lengths = p1_messages['message'].str.len()
        p2_lengths = p2_messages['message'].str.len()
        
        length_correlation = 0
        if len(p1_lengths) > 1 and len(p2_lengths) > 1:
            try:
                length_correlation = np.corrcoef(
                    p1_lengths.head(min(100, len(p1_lengths))), 
                    p2_lengths.head(min(100, len(p2_lengths)))
                )[0, 1]
                if np.isnan(length_correlation):
                    length_correlation = 0
            except Exception:
                length_correlation = 0
        
        return {
            'response_rate': response_rate,
            'message_balance': min(len(p1_messages), len(p2_messages)) / max(len(p1_messages), len(p2_messages), 1),
            'length_correlation': length_correlation,
            'strength_score': (response_rate + abs(length_correlation)) / 2
        }
    
    def _analyze_conversation_balance(self, df: pd.DataFrame) -> Dict:
        """Analyze conversation balance among participants"""
        participants = df['sender'].value_counts()
        total_messages = len(df)
        
        # Calculate balance metrics
        message_shares = participants / total_messages
        balance_score = 1 - message_shares.std()  # Lower std = better balance
        
        return {
            'balance_score': float(balance_score),
            'dominant_speaker': participants.index[0],
            'quiet_speaker': participants.index[-1],
            'dominance_ratio': float(participants.iloc[0] / participants.iloc[-1]) if len(participants) > 1 else 1.0,
            'participation_distribution': participants.to_dict()
        }
    
    def _extract_topics_for_period(self, messages: List[str], n_topics: int = 5) -> List[Dict]:
        """Extract topics for a specific time period"""
        try:
            if len(messages) < 10:
                return []
            
            # Use LDA for topic modeling
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(messages)
            
            n_topics = min(n_topics, len(messages) // 5)  # Adjust based on data size
            if n_topics < 1:
                return []
            
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=10)
            lda.fit(tfidf_matrix)
            
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words = [feature_names[i] for i in topic.argsort()[-5:][::-1]]
                topics.append({
                    'topic_id': topic_idx,
                    'keywords': top_words,
                    'weight': float(topic.sum())
                })
            
            return sorted(topics, key=lambda x: x['weight'], reverse=True)
            
        except Exception:
            return []
    
    def _identify_trending_topics(self, topic_timeline: List[Dict]) -> Dict:
        """Identify trending topics over time"""
        trending = {'rising': [], 'declining': [], 'consistent': []}
        
        try:
            # Track keyword frequency over time
            keyword_timeline = defaultdict(list)
            
            for period in topic_timeline:
                period_keywords = set()
                for topic in period.get('topics', []):
                    period_keywords.update(topic.get('keywords', []))
                
                for keyword in period_keywords:
                    keyword_timeline[keyword].append(1)
                
                # Fill zeros for keywords not present in this period
                for keyword in keyword_timeline:
                    if keyword not in period_keywords:
                        keyword_timeline[keyword].append(0)
            
            # Analyze trends
            for keyword, timeline in keyword_timeline.items():
                if len(timeline) < 3:
                    continue
                
                # Simple trend analysis
                recent_avg = np.mean(timeline[-3:])
                early_avg = np.mean(timeline[:3])
                
                if recent_avg > early_avg * 1.5:
                    trending['rising'].append({'keyword': keyword, 'growth': recent_avg / max(early_avg, 0.1)})
                elif recent_avg < early_avg * 0.5:
                    trending['declining'].append({'keyword': keyword, 'decline': early_avg / max(recent_avg, 0.1)})
                elif abs(recent_avg - early_avg) < 0.3:
                    trending['consistent'].append({'keyword': keyword, 'stability': 1 - abs(recent_avg - early_avg)})
            
        except Exception:
            pass
        
        return trending
    
    def _analyze_topic_transitions(self, topic_timeline: List[Dict]) -> List[Dict]:
        """Analyze how topics transition over time"""
        transitions = []
        
        try:
            for i in range(1, len(topic_timeline)):
                prev_topics = set()
                curr_topics = set()
                
                for topic in topic_timeline[i-1].get('topics', []):
                    prev_topics.update(topic.get('keywords', []))
                
                for topic in topic_timeline[i].get('topics', []):
                    curr_topics.update(topic.get('keywords', []))
                
                # Calculate transition metrics
                overlap = len(prev_topics & curr_topics)
                new_topics = curr_topics - prev_topics
                dropped_topics = prev_topics - curr_topics
                
                transitions.append({
                    'from_period': topic_timeline[i-1]['period'],
                    'to_period': topic_timeline[i]['period'],
                    'topic_overlap': overlap,
                    'new_topics': list(new_topics)[:5],
                    'dropped_topics': list(dropped_topics)[:5],
                    'continuity_score': overlap / max(len(prev_topics | curr_topics), 1)
                })
                
        except Exception:
            pass
        
        return transitions
    
    def _analyze_topic_lifecycle(self, topic_timeline: List[Dict]) -> Dict:
        """Analyze the lifecycle of topics"""
        lifecycle = {'birth_rate': 0, 'death_rate': 0, 'avg_lifespan': 0, 'topic_evolution': []}
        
        try:
            # Track when topics appear and disappear
            topic_appearances = defaultdict(list)
            
            for i, period in enumerate(topic_timeline):
                period_topics = set()
                for topic in period.get('topics', []):
                    period_topics.update(topic.get('keywords', []))
                
                for topic_word in period_topics:
                    topic_appearances[topic_word].append(i)
            
            # Calculate lifecycle metrics
            birth_count = 0
            death_count = 0
            lifespans = []
            
            for topic_word, appearances in topic_appearances.items():
                if len(appearances) > 1:
                    lifespan = max(appearances) - min(appearances) + 1
                    lifespans.append(lifespan)
                    
                    if min(appearances) > 0:  # Born after start
                        birth_count += 1
                    if max(appearances) < len(topic_timeline) - 1:  # Died before end
                        death_count += 1
            
            lifecycle['birth_rate'] = birth_count / max(len(topic_timeline), 1)
            lifecycle['death_rate'] = death_count / max(len(topic_timeline), 1)
            lifecycle['avg_lifespan'] = np.mean(lifespans) if lifespans else 0
            
        except Exception:
            pass
        
        return lifecycle
    
    def _analyze_seasonal_topic_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze seasonal patterns in topics"""
        seasonal = {}
        
        try:
            for month in range(1, 13):
                month_data = df[df['timestamp'].dt.month == month]
                if len(month_data) > 10:
                    month_messages = month_data['message'].tolist()
                    month_topics = self._extract_topics_for_period(month_messages, 3)
                    seasonal[f'month_{month}'] = month_topics[:3]  # Top 3 topics
                    
        except Exception:
            pass
        
        return seasonal
    
    def _get_most_common_mood(self, hour_data: pd.DataFrame) -> str:
        """Get most common mood for hour data"""
        try:
            moods = []
            for _, row in hour_data.iterrows():
                sentiment = row['sentiment']
                intensity = row.get('emotion_intensity', 0)
                moods.append(self._categorize_mood(sentiment, intensity))
            
            if moods:
                return Counter(moods).most_common(1)[0][0]
            return 'neutral'
            
        except Exception:
            return 'neutral'
    
    def _find_best_mood_day(self, participant_data: pd.DataFrame, mood_type: str) -> str:
        """Find the day with best/worst mood for participant"""
        try:
            daily_mood = participant_data.groupby(participant_data['timestamp'].dt.date)['sentiment'].mean()
            
            if mood_type == 'positive':
                best_day = daily_mood.idxmax()
            else:  # negative
                best_day = daily_mood.idxmin()
            
            return str(best_day)
            
        except Exception:
            return "N/A"
    
    def _analyze_mood_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze mood trends over time"""
        trends = {}
        
        try:
            # Weekly mood trends
            df['week'] = df['timestamp'].dt.to_period('W')
            weekly_mood = df.groupby('week')['sentiment'].mean()
            
            if len(weekly_mood) > 1:
                # Calculate trend direction
                x = np.arange(len(weekly_mood))
                y = weekly_mood.values
                slope = np.polyfit(x, y, 1)[0]
                
                trends['overall_trend'] = 'improving' if slope > 0.01 else 'declining' if slope < -0.01 else 'stable'
                trends['trend_strength'] = abs(slope)
                trends['weekly_mood_avg'] = float(weekly_mood.mean())
                trends['mood_volatility'] = float(weekly_mood.std())
            
        except Exception:
            pass
        
        return trends
    
    def _identify_emotional_events(self, df: pd.DataFrame) -> List[Dict]:
        """Identify significant emotional events"""
        events = []
        
        try:
            # Find days with extreme sentiment spikes
            daily_sentiment = df.groupby(df['timestamp'].dt.date)['sentiment'].mean()
            
            # Identify outliers
            mean_sentiment = daily_sentiment.mean()
            std_sentiment = daily_sentiment.std()
            
            for date, sentiment in daily_sentiment.items():
                if abs(sentiment - mean_sentiment) > 2 * std_sentiment:
                    event_type = 'very_positive' if sentiment > mean_sentiment else 'very_negative'
                    day_messages = df[df['timestamp'].dt.date == date]
                    
                    events.append({
                        'date': str(date),
                        'type': event_type,
                        'sentiment_score': float(sentiment),
                        'message_count': len(day_messages),
                        'participants': day_messages['sender'].unique().tolist()
                    })
                    
        except Exception:
            pass
        
        return events[:10]  # Limit to top 10 events
    
    def _analyze_mood_synchronization(self, df: pd.DataFrame) -> Dict:
        """Analyze mood synchronization between participants"""
        sync = {}
        
        try:
            participants = df['sender'].unique()
            
            for i, p1 in enumerate(participants):
                for p2 in participants[i+1:]:
                    p1_data = df[df['sender'] == p1]
                    p2_data = df[df['sender'] == p2]
                    
                    # Align by date
                    p1_daily = p1_data.groupby(p1_data['timestamp'].dt.date)['sentiment'].mean()
                    p2_daily = p2_data.groupby(p2_data['timestamp'].dt.date)['sentiment'].mean()
                    
                    # Find common dates
                    common_dates = set(p1_daily.index) & set(p2_daily.index)
                    
                    if len(common_dates) > 3:
                        p1_aligned = [p1_daily[date] for date in common_dates]
                        p2_aligned = [p2_daily[date] for date in common_dates]
                        
                        # Calculate correlation
                        correlation = np.corrcoef(p1_aligned, p2_aligned)[0, 1]
                        if not np.isnan(correlation):
                            sync[f'{p1}-{p2}'] = {
                                'correlation': float(correlation),
                                'sync_strength': 'high' if abs(correlation) > 0.7 else 'medium' if abs(correlation) > 0.4 else 'low',
                                'common_days': len(common_dates)
                            }
                            
        except Exception:
            pass
        
        return sync
    
    def _generate_behavioral_insights(self, user_behavior: Dict) -> List[str]:
        """Generate behavioral insights from user behavior data"""
        insights = []
        
        try:
            for user, behavior in user_behavior.items():
                msg_count = behavior.get('total_messages', 0)
                avg_length = behavior.get('avg_message_length', 0)
                
                if msg_count > 1000:
                    insights.append(f"{user} is highly active with {msg_count:,} messages")
                
                if avg_length > 100:
                    insights.append(f"{user} tends to write long, detailed messages")
                elif avg_length < 20:
                    insights.append(f"{user} prefers brief, concise communication")
                    
        except Exception:
            pass
        
        return insights
    
    def _generate_relationship_insights(self, relationship_dynamics: Dict) -> List[str]:
        """Generate relationship insights"""
        insights = []
        
        try:
            if 'relationship_strength' in relationship_dynamics:
                for pair, strength in relationship_dynamics['relationship_strength'].items():
                    if strength.get('strength_score', 0) > 0.8:
                        insights.append(f"Strong relationship detected between {pair.replace('-', ' and ')}")
                        
        except Exception:
            pass
        
        return insights
    
    def _generate_temporal_insights(self, mood_tracking: Dict, patterns: Dict) -> List[str]:
        """Generate temporal insights"""
        insights = []
        
        try:
            # Mood insights
            if 'hourly_patterns' in mood_tracking:
                best_hour = max(mood_tracking['hourly_patterns'].items(), 
                              key=lambda x: x[1].get('average_sentiment', 0))
                insights.append(f"Most positive conversations happen around {best_hour[0]}:00")
                
        except Exception:
            pass
        
        return insights
    
    def _generate_communication_insights(self, summaries: Dict) -> List[str]:
        """Generate communication insights"""
        insights = []
        
        try:
            if 'conversation_segments' in summaries:
                avg_duration = np.mean([seg.get('duration_minutes', 0) 
                                      for seg in summaries['conversation_segments']])
                insights.append(f"Average conversation duration: {avg_duration:.1f} minutes")
                
        except Exception:
            pass
        
        return insights
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            # Based on mood tracking
            if 'mood_tracking' in analysis_results:
                mood_data = analysis_results['mood_tracking']
                if 'participant_moods' in mood_data:
                    for participant, mood_info in mood_data['participant_moods'].items():
                        if mood_info.get('negative_ratio', 0) > 0.4:
                            recommendations.append(f"Consider checking on {participant} - showing signs of stress")
                            
        except Exception:
            pass
        
        return recommendations
    
    def _detect_anomalies(self, analysis_results: Dict, chat_data: List[Dict]) -> List[Dict]:
        """Detect anomalies in conversation patterns"""
        anomalies = []
        
        try:
            df = pd.DataFrame(chat_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Message frequency anomalies
            daily_counts = df.groupby(df['timestamp'].dt.date).size()
            mean_daily = daily_counts.mean()
            std_daily = daily_counts.std()
            
            for date, count in daily_counts.items():
                if count > mean_daily + 3 * std_daily:
                    anomalies.append({
                        'type': 'high_activity_anomaly',
                        'date': str(date),
                        'message_count': int(count),
                        'description': f"Unusually high activity: {count} messages"
                    })
                    
        except Exception:
            pass
        
        return anomalies[:5]  # Limit to top 5 anomalies
