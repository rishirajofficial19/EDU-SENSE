"""
Resource management for learning gap recommendations.
Loads website and YouTube links from external files.
YouTube links are customized based on class level.
"""

import os
import re

# Path to resource files
RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(RESOURCE_DIR)

# Resource files should be in the same directory as this script
POSSIBLE_DOWNLOAD_DIRS = [RESOURCE_DIR]

# Find the resource files
WEBSITE_LINKS_FILE = None
YOUTUBE_LINKS_FILE = None

for download_dir in POSSIBLE_DOWNLOAD_DIRS:
    website_file = os.path.join(download_dir, "EDU-SENCE link.txt")
    youtube_file = os.path.join(download_dir, "EDU-SENCE link(1).txt")
    
    if os.path.exists(website_file) and os.path.exists(youtube_file):
        WEBSITE_LINKS_FILE = website_file
        YOUTUBE_LINKS_FILE = youtube_file
        break

# Fallback to first found file
if WEBSITE_LINKS_FILE is None:
    for download_dir in POSSIBLE_DOWNLOAD_DIRS:
        website_file = os.path.join(download_dir, "EDU-SENCE link.txt")
        if os.path.exists(website_file):
            WEBSITE_LINKS_FILE = website_file
            break

if YOUTUBE_LINKS_FILE is None:
    for download_dir in POSSIBLE_DOWNLOAD_DIRS:
        youtube_file = os.path.join(download_dir, "EDU-SENCE link(1).txt")
        if os.path.exists(youtube_file):
            YOUTUBE_LINKS_FILE = youtube_file
            break


def parse_resource_file(filepath):
    """
    Parse resource file and return dictionary with subject -> links mapping.
    """
    resources = {}
    
    if not os.path.exists(filepath):
        return resources
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Handle both Unix (\n) and Windows (\r\n) line endings
        lines = content.replace('\r\n', '\n').split('\n')
        current_subject = None
        current_links = []
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if not line:
                continue
            
            # Remove extra spaces
            line_clean = ' '.join(line.split())
            
            # Detect subject line: contains '-' and left side doesn't start with number
            if '-' in line_clean:
                # Find the dash position
                dash_idx = line_clean.find('-')
                left_part = line_clean[:dash_idx].strip()
                right_part = line_clean[dash_idx+1:].strip()
                
                # Check if left part looks like a subject (alphabetic)
                if left_part and not left_part[0].isdigit() and left_part.replace(' ', '').isalpha():
                    # This is a subject line
                    # Save previous subject
                    if current_subject and current_links:
                        resources[current_subject] = current_links.copy()
                    
                    current_subject = left_part.lower()
                    current_links = []
                    
                    # Extract URL from right part
                    if right_part:
                        # Could be "1. https://..." or "https://..." or "https://..."
                        if right_part[0].isdigit() and '.' in right_part:
                            # Format: "1. https://..."
                            url = right_part.split('.', 1)[1].strip()
                            if url.startswith('http'):
                                current_links.append(url)
                        elif right_part.startswith('http'):
                            current_links.append(right_part)
                    continue
            
            # Check if this is a URL line (for numbered items in list)
            if line_clean[0].isdigit() and '.' in line_clean:
                # Format: "2. https://..."
                if current_subject:
                    url = line_clean.split('.', 1)[1].strip()
                    if url.startswith('http'):
                        current_links.append(url)
            
            # Check if this is a standalone URL
            elif line_clean.startswith('http'):
                if current_subject:
                    current_links.append(line_clean)
        
        # Don't forget last subject
        if current_subject and current_links:
            resources[current_subject] = current_links
            
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        import traceback
        traceback.print_exc()
    
    return resources


# Load resources on module import
WEBSITE_RESOURCES = parse_resource_file(WEBSITE_LINKS_FILE)
YOUTUBE_RESOURCES = parse_resource_file(YOUTUBE_LINKS_FILE)


def normalize_subject(subject):
    """Normalize subject name for matching."""
    normalized = subject.lower().strip()
    
    # Fix common typos
    normalized = normalized.replace('scirnce', 'science')
    normalized = normalized.replace('sience', 'science')
    
    # Handle aliases
    aliases = {
        'maths': 'maths',
        'math': 'maths',
        'arithmetic': 'maths',
        'fractions': 'maths',
        'algebra': 'maths',
        'geometry': 'maths',
        'data analysis': 'maths',
        'statistics': 'maths',
        'sst': 'social science',
        'social studies': 'social science',
        'cs': 'computer science',
        'programming': 'computer science',
    }
    
    return aliases.get(normalized, normalized)


def get_website_links_for_topic(topic):
    """
    Get website resource links for a specific topic.
    
    Args:
        topic: Subject/topic name (e.g., "Algebra", "Fractions", "Maths")
        
    Returns:
        List of website URLs for the topic
    """
    normalized = normalize_subject(topic)
    
    # Try exact match
    if normalized in WEBSITE_RESOURCES:
        return WEBSITE_RESOURCES[normalized]
    
    # Try partial match
    for subject, links in WEBSITE_RESOURCES.items():
        if normalized in subject or subject in normalized:
            return links
    
    return []


def get_youtube_links_for_topic(topic, class_level=None):
    """
    Get YouTube search links for a specific topic, customized for class.
    Creates direct YouTube search results with subject + class + channel.
    
    Args:
        topic: Subject/topic name (e.g., "Algebra", "Maths")
        class_level: Class/grade level (e.g., 9, 10, "Class 9")
                     Will be added to search queries
        
    Returns:
        List of YouTube search URLs with subject + class + channel
    """
    normalized = normalize_subject(topic)
    
    # Get base channel links
    links = []
    if normalized in YOUTUBE_RESOURCES:
        links = YOUTUBE_RESOURCES[normalized].copy()
    else:
        # Try partial match
        for subject, subj_links in YOUTUBE_RESOURCES.items():
            if normalized in subject or subject in normalized:
                links = subj_links.copy()
                break
    
    # Create search URLs with subject + class + channel
    if class_level and links:
        class_num = str(class_level).replace('class', '').replace('Class', '').strip()
        customized_links = []
        
        for link in links:
            # Extract channel name from different URL formats
            channel_name = None
            if '@' in link:
                # Format: https://www.youtube.com/@ChannelName
                channel_name = link.split('@')[-1].split('/')[0]
            elif 'youtube.com/c/' in link:
                # Format: https://www.youtube.com/c/ChannelName
                channel_name = link.split('/c/')[-1].split('/')[0]
            
            # Create search URL with subject + class + channel
            if channel_name:
                search_query = f"{topic} class {class_num} {channel_name}".replace(' ', '+')
                customized_url = f"https://www.youtube.com/results?search_query={search_query}"
            else:
                # Fallback: just search for subject + class
                search_query = f"{topic} class {class_num}".replace(' ', '+')
                customized_url = f"https://www.youtube.com/results?search_query={search_query}"
            
            customized_links.append(customized_url)
        
        return customized_links
    elif links:
        # If no class level, create basic search URLs with channels
        customized_links = []
        for link in links:
            channel_name = None
            if '@' in link:
                channel_name = link.split('@')[-1].split('/')[0]
            elif 'youtube.com/c/' in link:
                channel_name = link.split('/c/')[-1].split('/')[0]
            
            if channel_name:
                search_query = f"{topic} {channel_name}".replace(' ', '+')
            else:
                search_query = topic.replace(' ', '+')
            
            customized_url = f"https://www.youtube.com/results?search_query={search_query}"
            customized_links.append(customized_url)
        
        return customized_links
    
    return links


def get_resources_for_topic(topic, class_level=None):
    """
    Get all resources (websites + YouTube) for a topic.
    
    Args:
        topic: Subject/topic name
        class_level: Optional class level for YouTube customization
        
    Returns:
        Dictionary with 'websites' and 'videos' keys
    """
    return {
        'websites': get_website_links_for_topic(topic),
        'videos': get_youtube_links_for_topic(topic, class_level)
    }


def get_all_resources():
    """Get all available resources."""
    return {
        'websites': WEBSITE_RESOURCES,
        'youtube': YOUTUBE_RESOURCES
    }
