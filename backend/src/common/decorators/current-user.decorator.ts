import { createParamDecorator, type ExecutionContext } from '@nestjs/common';
import type { AuthenticatedRequest } from '../types/authenticated-request.js';

/**
 * Extrae el usuario autenticado (`req.user`) adjuntado por JwtAuthGuard.
 * Uso: `@CurrentUser() user: AuthUser` en un handler protegido por @UseGuards(JwtAuthGuard).
 */
export const CurrentUser = createParamDecorator(
  (_data: unknown, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest<AuthenticatedRequest>();
    return request.user;
  },
);
