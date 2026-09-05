import type { Request } from 'express';
import type { MembershipModel } from '../../generated/prisma/models.js';

/** Payload que el JwtStrategy adjunta a la request tras validar el access token. */
export interface AuthUser {
  userId: string;
  email: string;
}

/** Request de Express enriquecida por los guards de autenticación/autorización. */
export interface AuthenticatedRequest extends Request {
  user: AuthUser;
  /** Presente solo cuando la ruta pasó por MembershipGuard. */
  membership?: MembershipModel;
}
