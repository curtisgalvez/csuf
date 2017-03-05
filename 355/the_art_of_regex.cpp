#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <regex>
#include <string>
#include <time.h>

int main()
{
    clock_t start = clock();
    std::ifstream input;
    std::map<std::string, int> words;
    std::map<char, int> alpha;
    std::stringstream data;
    std::string text, word;
    std::vector<std::string> word_list;

    input.open("input");
    if (input.is_open())
    {
        data << input.rdbuf();
        text = std::regex_replace(data.str(), std::regex ("([^a-zA-Z\\s])"), " ");
        text = std::regex_replace(text, std::regex ("(['])"), "");
    }
    input.close();

    //http://www.cplusplus.com/reference/
    //http://stackoverflow.com/questions/19887232/how-to-loop-through-a-string-by-space-how-do-i-know-the-index-no-of-the-word-i
    for (std::stringstream s(text); s >> word;)
    {
        std::string temp;
        temp.resize(word.size());
        std::transform(word.begin(), word.end(), temp.begin(), ::tolower);
        if (words.count(temp) == 0)
        {
            words.insert(std::pair<std::string, int>(temp, 1));
        }
        else
        {
            words[temp]++;
        }
        for (unsigned i = 0; i < temp.length(); i++)
        {
            if (alpha.count(temp[i]) == 0)
            {
                alpha.insert(std::pair<char, int>(temp[i], 1));
            }
            else
            {
                alpha[temp[i]]++;
            }
        }
    }

    word_list.push_back("");
    for (std::map<std::string, int>::iterator it = words.begin(); it != words.end(); it++)
    {
        std::string current_word = it->first;
        std::string long_word = word_list.front();
        // std::cout << it->first << std::endl;
        if (current_word.length() > long_word.length())
        {
            word_list.clear();
            word_list.push_back(current_word);
        }
        else if (current_word.length() == long_word.length())
        {
            word_list.push_back(current_word);
        }
    }
    std::cout << "Letter frequency:" << std::endl;
    for (std::map<char, int>::iterator it = alpha.begin(); it != alpha.end(); it++)
    {
        std::cout << "\t" << it->first << " - " << it->second << std::endl;
    }
    std::cout << "The word \"the\" appears " << words["the"] << " times." << std::endl;
    std::cout << "The word \"principles\" appears " << words["principles"] << " times." << std::endl;
    std::cout << "The longest word(s) at length " << word_list[0].length() << std::endl;
    for (unsigned i = 0; i < word_list.size(); i++)
    {
        std::cout << "\t" << word_list[i] << std::endl;
    }
    std::cout << (float(clock()) - float(start)) / CLOCKS_PER_SEC << std::endl;

    return 0;
}