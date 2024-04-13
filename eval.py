# coding: UTF-8
import time
import torch
import numpy as np
from train_eval import train, init_network
from importlib import import_module
from utils_fasttext import build_dataset, build_iterator, get_time_dif
import argparse
import pickle as pkl

class NewsClassifier:
    def __init__(self):
        print("NewsClassifier initializing!")
        self.parser = argparse.ArgumentParser(description='Chinese Text Classification')
        self.args = self.parser.parse_args()
        self.args.model = "FastText"
        self.args.embedding = 'random'
        self.args.word = False
        self.dataset = 'THUCNews'  # 数据集
        # 搜狗新闻:embedding_SougouNews.npz, 腾讯:embedding_Tencent.npz, 随机初始化:random
        self.embedding = 'random'
        self.model_name = 'FastText'   # 'TextRCNN'  # TextCNN, TextRNN, FastText, TextRCNN, TextRNN_Att, DPCNN, Transformer
        self.labels = ["finance","realty","stocks","education","science","society","politics","sports","game","entertainment"]

        x = import_module('models.' + self.model_name)
        self.config = x.Config(self.dataset, self.embedding)
        np.random.seed(1)
        torch.manual_seed(1)
        torch.cuda.manual_seed_all(1)
        torch.backends.cudnn.deterministic = True  # 保证每次结果一样

        start_time = time.time()
        print("Loading data...")
        vocab, _, _, _ = build_dataset(self.config, self.args.word)
        time_dif = get_time_dif(start_time)
        print("Finished!")
        print("Time usage:", time_dif)

        # eval
        self.config.n_vocab = len(vocab)
        self.model = x.Model(self.config).to(self.config.device)
        if self.model_name != 'Transformer':
            init_network(self.model)
        # print(model.parameters)

    def my_to_tensor(self, config ,datas):
        # xx = [xxx[2] for xxx in datas]
        # indexx = np.argsort(xx)[::-1]
        # datas = np.array(datas)[indexx]
        x = torch.LongTensor([_[0] for _ in datas]).to(config.device)
        y = torch.LongTensor([_[1] for _ in datas]).to(config.device)
        bigram = torch.LongTensor([_[3] for _ in datas]).to(config.device)
        trigram = torch.LongTensor([_[4] for _ in datas]).to(config.device)

        # pad前的长度(超过pad_size的设为pad_size)
        seq_len = torch.LongTensor([_[2] for _ in datas]).to(config.device)
        return (x, seq_len, bigram, trigram)

    def str2numpy(self, text, config):
        UNK, PAD = '<UNK>', '<PAD>'
        tokenizer = lambda x: [y for y in x]  # char-level
        vocab = pkl.load(open(config.vocab_path, 'rb'))

        def biGramHash(sequence, t, buckets):
            t1 = sequence[t - 1] if t - 1 >= 0 else 0
            return (t1 * 14918087) % buckets

        def triGramHash(sequence, t, buckets):
            t1 = sequence[t - 1] if t - 1 >= 0 else 0
            t2 = sequence[t - 2] if t - 2 >= 0 else 0
            return (t2 * 14918087 * 18408749 + t1 * 14918087) % buckets

        def to_numpy(content, pad_size=32):
            words_line = []
            token = tokenizer(content)
            seq_len = len(token)
            if pad_size:
                if len(token) < pad_size:
                    token.extend([PAD] * (pad_size - len(token)))
                else:
                    token = token[:pad_size]
                    seq_len = pad_size
            # word to id
            for word in token:
                words_line.append(vocab.get(word, vocab.get(UNK)))

            # fasttext ngram
            buckets = config.n_gram_vocab
            bigram = []
            trigram = []
            # ------ngram------
            for i in range(pad_size):
                bigram.append(biGramHash(words_line, i, buckets))
                trigram.append(triGramHash(words_line, i, buckets))
            # -----------------
            return [(words_line, -1, seq_len, bigram, trigram)]
        
        npy = to_numpy(text, config.pad_size)
        npy = self.my_to_tensor(config, npy)
        return npy

    def test(self, config, texts):
        # test
        self.model.load_state_dict(torch.load(config.save_path, map_location='cpu'))
        self.model.eval()
        data = self.str2numpy(texts, config)
        outputs = self.model(data)
        predic = torch.max(outputs.data, 1)[1].cpu().numpy()[0]
        cls = self.labels[predic]
        return cls

    # python eval.py --model FastText --embedding random 
    def classify(self, title):
        return self.test(self.config, title)

if __name__ == '__main__' :
    classfier = NewsClassifier()
    title = '图文：借贷成本上涨致俄罗斯铝业净利下滑21%'
    print(classfier.classify(title))

