#pragma once

#define PI 3.1415f

struct Vec3 {
    float x, y, z;
};

// ---------------------
// Variáveis de câmera
// ---------------------
extern float cameraX;
extern float cameraY;
extern float cameraZ;

extern float horizontalAngle;
extern float verticalAngle;
extern float speed;

extern float directionX;
extern float directionY;
extern float directionZ;

extern float rightVectorX;
extern float rightVectorZ; 

extern float upVector[3];

// ---------------------
// controle de tempo
// ---------------------
extern double lastTime;
extern float deltaTime;
extern float waterTime;

// ---------------------
// constantes do terreno
// ---------------------
extern const int TERRAIN_SIZE;
extern const float HEIGHT_SCALE;
extern const float MAX_HEIGHT;
extern const float WATER_HEIGHT;

// textura / splatting heights
extern const float SNOW_HEIGHT_START;
extern const float ROCK_HEIGHT_START;

// funções
void calculateDirectionVectors();
Vec3 crossProduct(Vec3 v1, Vec3 v2);
Vec3 normalize(Vec3 v);
float getTerrainHeight(float x, float z, float centerX, float centerZ, float radius);
void applyHeightColor(float height, float maxHeight);
void drawProceduralMountain(float centerX, float centerZ, float radius);
void drawWaterPlane(bool isReflectionPass);
void renderMountains();