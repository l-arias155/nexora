import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module.js';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.setGlobalPrefix('api');
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // descarta propiedades no declaradas en los DTO
      forbidNonWhitelisted: true, // rechaza el request si vienen propiedades extra
      transform: true, // castea payloads a las clases DTO (útil para tipos/enum)
    }),
  );

  await app.listen(process.env.PORT ?? 3000);
}
await bootstrap();
