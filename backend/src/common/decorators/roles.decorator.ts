import { SetMetadata } from '@nestjs/common';
import type { MembershipRole } from '../../generated/prisma/enums.js';

export const ROLES_KEY = 'roles';

/**
 * Marca un handler con los roles de Membership permitidos para ejecutarlo.
 * Debe combinarse con MembershipGuard, que es quien realmente lee este
 * metadato y valida el rol del usuario en la organización de la request.
 */
export const Roles = (...roles: MembershipRole[]) =>
  SetMetadata(ROLES_KEY, roles);
