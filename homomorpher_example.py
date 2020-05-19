import homomorpher

if __name__ == '__main__':
    z = homomorpher.generate_random_z()
    homomorpher.generate_img(z, 1)
    homomorpher.transform_img(z, 1, 'SVM_summerlakes')
