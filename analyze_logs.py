import re

def read_and_group_log_entries(log_file_path):
    with open(log_file_path, 'r', encoding='utf-8') as file:
        grouped_entries = []
        current_entry = ""
        for line in file:
            # Check if line starts with a timestamp (indicating a new log entry)
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}', line):
                if current_entry:  # if there's a current entry, add it to the list
                    grouped_entries.append(current_entry)
                    current_entry = line  # start a new entry
                else:
                    current_entry = line
            else:
                current_entry += line  # continue adding lines to the current entry
        if current_entry:  # add the last entry
            grouped_entries.append(current_entry)
        return grouped_entries
def extract_spam_scores(grouped_entries):
    entries_with_scores = []
    pattern = re.compile(r'Spam score: (\d{1,3})')
    for entry in grouped_entries:
        match = pattern.search(entry)
        if match:
            spam_score = match.group(1)
            entries_with_scores.append((entry, spam_score))
    return entries_with_scores

def sort_entries_by_recipient(entries_with_scores, recipient_emails):
    sorted_entries = {email: [] for email in recipient_emails}
    for entry, score in entries_with_scores:
        for email in recipient_emails:
            if f'X-StartMail-Original-To: {email}' in entry:
                sorted_entries[email].append((entry, score))
                break
    return sorted_entries


def extract_score(log_entry):
    """
    Extracts the score value from a log entry.
    The score is expected to be in the format 'score=-0.2' where -0.2 is an example value.
    """
    score_pattern = re.compile(r'score=([-\d.]+)')
    match = score_pattern.search(log_entry)
    if match:
        return float(match.group(1))
    else:
        return None  # or an appropriate default/fallback value

# Path to your log file
log_file_path = 'app.log'
recipient_emails = ["****@use.startmail.com", "****@use.startmail.com"]
#TODO

# Process the log file
grouped_entries = read_and_group_log_entries(log_file_path)
entries_with_scores = extract_spam_scores(grouped_entries)
sorted_entries = sort_entries_by_recipient(entries_with_scores, recipient_emails)

# Print the sorted entries with spam scores

for email, entries in sorted_entries.items():
    print(f"Entries for {email}:")
    spam_counter = 0
    no_spam_counter = 0
    for entry, score in entries:
        div_index = entry.find('<div')
        if div_index != -1:
            entry = entry[div_index:]  # Cut off everything before <div
        print(f"Spam score: {score}")
        if int(score) < 30:
            no_spam_counter += 1
            print(entry)
        else:
            spam_counter += 1
            print(extract_score(entry))
            print(entry)
        print("-----")
    print(f"Spam: {spam_counter}")
    print(f"No Spam: {no_spam_counter}")
