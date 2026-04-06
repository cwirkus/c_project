#include <stdlib.h>
#include <stdio.h>

typedef struct {
    float weight;
    float bias;
    float learning_rate;
} Model;

Model* create_model(float lr) {
    Model* m = (Model*)malloc(sizeof(Model));
    m->weight = 0.0f;
    m->bias   = 0.0f;
    m->learning_rate = lr;
    return m;
}

float predict(Model* m, float input) {
    return (input * m->weight) + m->bias;
}

void train_step(Model* m, float input, float expected) {
    float prediction = predict(m, input);
    float error = expected - prediction;
    m->weight += m->learning_rate * error * input;
    m->bias   += m->learning_rate * error;
}

void free_model(Model* m) {
    free(m);
}
