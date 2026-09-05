import { Injectable } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

/**
 * Exige un access token JWT válido (ver JwtStrategy). Adjunta el resultado
 * de `JwtStrategy.validate` a `req.user`.
 */
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}
